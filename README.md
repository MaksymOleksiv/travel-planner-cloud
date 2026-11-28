# Travel Planner API — розгортання в AWS

REST API для планування подорожей: користувач створює **проєкти** (поїздки) і додає до них **місця** для відвідування, відмічає відвідані; проєкт автоматично стає `completed`, коли всі місця відвідані.

Лабораторна робота 1 з курсу хмарних технологій: застосунок у контейнері, інфраструктура як код (Terraform), керована база, балансувальник і автоматичний деплой з GitHub.

## Публічна адреса

| | URL |
|---|---|
| API | http://travel-planner-alb-1039128351.eu-north-1.elb.amazonaws.com |
| Swagger UI | http://travel-planner-alb-1039128351.eu-north-1.elb.amazonaws.com/docs |
| Health check | http://travel-planner-alb-1039128351.eu-north-1.elb.amazonaws.com/health |

> Адреса змінюється після `terraform destroy` + `apply`; актуальна — у `terraform output app_url`.
> Лише HTTP: для HTTPS потрібен власний домен і сертифікат ACM.

## Технології

- **Застосунок:** Python 3.12, FastAPI, SQLAlchemy (async) + asyncpg, Alembic (міграції), JWT (PyJWT, bcrypt)
- **Контейнер:** Docker, Docker Compose
- **Хмара (AWS, регіон eu-north-1):** ECS Fargate (ARM64), RDS PostgreSQL 17, ECR, Application Load Balancer, VPC, Secrets Manager, CloudWatch, SNS, IAM (OIDC)
- **IaC:** Terraform
- **CI/CD:** GitHub Actions

## Архітектура

```
                         Інтернет
                            │  HTTP :80
                ┌───────────▼───────────┐
   VPC          │  Application LB       │  публічні підмережі (2 AZ)
 10.20.0.0/16   └───────────┬───────────┘
                            │ :8000  (тільки від SG балансувальника)
                ┌───────────▼───────────┐
                │  ECS Fargate task     │  публічні підмережі, вхід лише від ALB
                │  (FastAPI контейнер)  │──► ECR, Secrets Manager, CloudWatch Logs
                └───────────┬───────────┘
                            │ :5432  (тільки від SG застосунку)
                ┌───────────▼───────────┐
                │  RDS PostgreSQL       │  приватні підмережі, без публічної адреси
                └───────────────────────┘

 GitHub push ─► GitHub Actions ─(OIDC роль)─► ECR (тег = хеш коміту) ─► ECS rolling update
```

- **Мережа:** VPC з двома публічними (ALB, контейнери) і двома приватними (база) підмережами у двох зонах доступності. Приватні підмережі не мають маршруту в інтернет. NAT Gateway свідомо не використовується (≈$35/міс.): контейнери мають публічну IP лише для вихідного трафіку, вхідний закритий security group.
- **Firewall:** ланцюжок security groups `ALB (80 з інтернету) → app (8000 тільки від ALB SG) → db (5432 тільки від app SG)` — правила посилаються на групи, а не на IP.
- **Секрети:** пароль бази генерує RDS і зберігає в Secrets Manager; ключ підпису JWT генерує Terraform і теж кладе в Secrets Manager. ECS підставляє обидва в контейнер як змінні середовища. У коді, образі й репозиторії секретів немає.

## Структура проєкту

```
.
├── app/                        # код застосунку (FastAPI)
│   ├── main.py                 # точка входу, /health
│   ├── api/
│   │   ├── dependencies.py     # репозиторії, перевірка JWT (get_current_user)
│   │   └── v1/routes/          # auth, projects, project_places
│   ├── core/                   # config (змінні середовища), database, security (JWT, bcrypt)
│   ├── models/                 # SQLAlchemy-моделі: Project, ProjectPlace, User
│   ├── repositories/           # доступ до бази
│   ├── schemas/                # Pydantic-схеми запитів/відповідей
│   └── services/               # клієнт зовнішнього Art Institute API
├── alembic/                    # міграції бази (виконуються при старті контейнера)
├── Dockerfile                  # образ застосунку
├── docker-entrypoint.sh        # alembic upgrade head + uvicorn
├── compose.yaml                # локальний запуск: застосунок + PostgreSQL
├── scripts/push-image.sh       # збірка і push першого образу (викликається з Terraform)
├── terraform/                  # уся інфраструктура AWS
│   ├── versions.tf             # провайдери, регіон, зони доступності
│   ├── variables.tf            # параметри
│   ├── network.tf              # VPC, підмережі, Internet Gateway, маршрути
│   ├── security.tf             # security groups
│   ├── ecr.tf                  # реєстр образів + перший образ
│   ├── rds.tf                  # PostgreSQL
│   ├── secrets.tf              # ключ підпису JWT у Secrets Manager
│   ├── alb.tf                  # балансувальник, target group, health check
│   ├── ecs.tf                  # кластер, IAM-ролі, task definition, сервіс, логи
│   ├── github-oidc.tf          # OIDC-провайдер і роль для GitHub Actions
│   ├── monitoring.tf           # дашборд CloudWatch, алерти, SNS → email
│   ├── budget.tf               # бюджет зі сповіщенням на email
│   └── outputs.tf              # публічна адреса тощо
└── .github/workflows/deploy.yml  # CI/CD
```

## Запуск локально

Потрібен Docker.

```bash
cp .env.example .env      # задати DB_PASSWORD і JWT_SECRET
docker compose up --build
```

API: http://localhost:8000, Swagger: http://localhost:8000/docs.
Дані бази лежать у volume `pgdata` і переживають `docker compose down` (видаляються лише `docker compose down -v`).

### Dockerfile

- базовий образ із зафіксованою версією: `python:3.12.12-slim-bookworm`;
- `requirements.txt` копіюється і встановлюється **до** коду → при зміні коду шар із залежностями береться з кешу;
- процес працює від непривілейованого користувача `appuser` (uid 10001);
- при старті виконуються міграції (`alembic upgrade head`), потім `uvicorn`.

## Розгортання в AWS

Потрібні: AWS CLI з налаштованим IAM-користувачем, Terraform ≥ 1.10, Docker.

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # вказати alert_email
terraform init
terraform apply                                 # ~10-15 хв (найдовше — RDS)
terraform output app_url
```

`terraform apply` з порожнього акаунта створює все, включно з першим образом у ECR.
Після `apply` підтвердити підписку в листі від AWS SNS, щоб отримувати алерти.

Видалити все:

```bash
terraform destroy
```

## CI/CD

`.github/workflows/deploy.yml`, запускається на push у `main` (зміни лише в `terraform/` чи `*.md` деплой не запускають):

1. **Checkout** коду.
2. **Вхід в AWS через OIDC:** GitHub видає короткоживучий токен, AWS перевіряє його і дає тимчасові ключі ролі `travel-planner-github-deploy`. Роль може взяти лише цей репозиторій з гілки `main`. Збережених ключів доступу в GitHub немає — лише змінна `AWS_ROLE_ARN`.
3. **Збірка образу** (ARM64) і **push в ECR** з тегом = хеш коміту.
4. **Нова ревізія task definition** з новим образом.
5. **Оновлення ECS-сервісу** і очікування, поки новий контейнер пройде health check. Зламаний деплой автоматично відкочується (deployment circuit breaker).

Роль має мінімальні права: push лише в цей ECR-репозиторій, оновлення лише цього ECS-сервісу, `iam:PassRole` лише для двох ролей задачі.

Відкат на попередню версію — перезапустити workflow для старого коміту (`Actions → Deploy to AWS → Re-run`) або задеплоїти образ зі старим хешем.

## API

Повний список — у Swagger UI (`/docs`).

| Метод | Ендпоінт | Опис | Токен |
|---|---|---|---|
| POST | `/api/v1/auth/register` | реєстрація (email, пароль ≥ 8 символів) | — |
| POST | `/api/v1/auth/login` | вхід (form: `username`=email, `password`) → JWT | — |
| GET | `/api/v1/auth/me` | поточний користувач | ✅ |
| GET | `/api/v1/projects/` | список проєктів | — |
| GET | `/api/v1/projects/{id}` | проєкт з місцями | — |
| POST | `/api/v1/projects/` | створити проєкт | ✅ |
| PATCH | `/api/v1/projects/{id}` | змінити проєкт | ✅ |
| DELETE | `/api/v1/projects/{id}` | видалити (якщо немає відвіданих місць) | ✅ |
| GET | `/api/v1/projects/{id}/places/` | місця проєкту | — |
| POST | `/api/v1/projects/{id}/places/` | додати місце (макс. 10) | ✅ |
| PATCH | `/api/v1/projects/{id}/places/{place_id}` | нотатки / відмітка «відвідано» | ✅ |
| GET | `/health` | стан застосунку і зв'язку з базою | — |

Захищені ендпоінти без токена повертають **401**.

```bash
URL=http://travel-planner-alb-1039128351.eu-north-1.elb.amazonaws.com

curl -X POST $URL/api/v1/auth/register -H 'Content-Type: application/json' \
  -d '{"email":"me@example.com","password":"secret123"}'

TOKEN=$(curl -s -X POST $URL/api/v1/auth/login \
  -d 'username=me@example.com&password=secret123' | jq -r .access_token)

curl -X POST $URL/api/v1/projects/ \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"name":"Stockholm trip","start_date":"2026-12-10","place_external_ids":[27992]}'
```

У Swagger UI: кнопка **Authorize** → email і пароль → захищені запити йдуть з токеном.

> Назви місць беруться з публічного API Art Institute of Chicago. Він закритий Cloudflare-перевіркою для серверних запитів, тому в хмарі `ARTIC_API_ENABLED=false` і місце зберігається як `Artwork #<id>`.

## Моніторинг

- **Логи** контейнера — CloudWatch Logs, група `/ecs/travel-planner` (7 днів).
- **Дашборд** `travel-planner` (`terraform output dashboard_url`): запити за хвилину, помилки 5xx, латентність p50/p95, CPU і пам'ять, здорові/нездорові екземпляри, стан алертів.
- **Алерти на email** (через SNS):
  - більше 5 відповідей 5xx за хвилину;
  - жоден екземпляр не проходить health check 2 хвилини.

## Бюджет

AWS Budgets: $10 на місяць, листи при 50% і 100% фактичних витрат та при прогнозі понад 100%.
