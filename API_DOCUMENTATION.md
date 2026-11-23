# Travel Planner API Documentation

Base URL: `http://localhost:8000/api/v1`

## Authentication

Currently, no authentication is required.

## Response Format

All responses follow this structure:

**Success Response:**
```json
{
  "id": 1,
  "name": "Project Name",
  ...
}
```

**Error Response:**
```json
{
  "detail": "Error message"
}
```

## HTTP Status Codes

- `200 OK` - Successful GET/PATCH request
- `201 Created` - Successful POST request
- `204 No Content` - Successful DELETE request
- `400 Bad Request` - Validation error or business logic violation
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Invalid request body

---

## Projects Endpoints

### 1. List All Projects

**GET** `/projects/`

**Query Parameters:**
- `limit` (integer, optional): Number of items per page. Default: 20
- `offset` (integer, optional): Number of items to skip. Default: 0

**Success Response (200):**
```json
[
  {
    "id": 1,
    "name": "Chicago Art Tour",
    "description": "Visit famous artworks",
    "start_date": "2026-03-01",
    "status": "active",
    "created_at": "2026-02-20T14:00:00",
    "updated_at": "2026-02-20T14:00:00",
    "places": []
  }
]
```

**Example:**
```bash
GET /api/v1/projects/?limit=10&offset=0
```

---

### 2. Get Single Project

**GET** `/projects/{id}`

**Path Parameters:**
- `id` (integer): Project ID

**Success Response (200):**
```json
{
  "id": 1,
  "name": "Chicago Art Tour",
  "description": "Visit famous artworks",
  "start_date": "2026-03-01",
  "status": "active",
  "created_at": "2026-02-20T14:00:00",
  "updated_at": "2026-02-20T14:00:00",
  "places": [
    {
      "id": 1,
      "project_id": 1,
      "external_id": 4,
      "title": "Priest and Boy",
      "artist_display": "Lawrence Carmichael Earle\nAmerican, 1845-1921",
      "image_url": "https://www.artic.edu/iiif/2/1753b638-d4fb-8e45-3db9-92dde7f053da/full/max/0/default.jpg",
      "notes": null,
      "is_visited": false,
      "created_at": "2026-02-20T14:00:00",
      "updated_at": "2026-02-20T14:00:00"
    }
  ]
}
```

**Error Response (404):**
```json
{
  "detail": "Project not found"
}
```

**Example:**
```bash
GET /api/v1/projects/1
```

---

### 3. Create Project

**POST** `/projects/`

**Request Body:**
```json
{
  "name": "Chicago Art Tour",
  "description": "Visit famous artworks",
  "start_date": "2026-03-01",
  "place_external_ids": [4, 20684, 27992]
}
```

**Request Body Fields:**
- `name` (string, required): Project name (1-255 characters)
- `description` (string, optional): Project description
- `start_date` (string, optional): Start date in format "YYYY-MM-DD"
- `place_external_ids` (array of integers, optional): List of artwork IDs from Art Institute API (max 10)

**Success Response (201):**
```json
{
  "id": 1,
  "name": "Chicago Art Tour",
  "description": "Visit famous artworks",
  "start_date": "2026-03-01",
  "status": "active",
  "created_at": "2026-02-20T14:00:00",
  "updated_at": "2026-02-20T14:00:00",
  "places": [
    {
      "id": 1,
      "project_id": 1,
      "external_id": 4,
      "title": "Priest and Boy",
      "artist_display": "Lawrence Carmichael Earle\nAmerican, 1845-1921",
      "image_url": "https://www.artic.edu/iiif/2/1753b638-d4fb-8e45-3db9-92dde7f053da/full/max/0/default.jpg",
      "notes": null,
      "is_visited": false,
      "created_at": "2026-02-20T14:00:00",
      "updated_at": "2026-02-20T14:00:00"
    }
  ]
}
```

**Error Response (400):**
```json
{
  "detail": "Cannot add more than 10 places to a project"
}
```

**Validation Rules:**
- Maximum 10 places per project
- All external_ids must be positive integers
- Each external_id must exist in Art Institute API
- Name is required and cannot be empty

**Example:**
```bash
POST /api/v1/projects/
Content-Type: application/json

{
  "name": "Chicago Art Tour",
  "description": "Visit famous artworks",
  "start_date": "2026-03-01",
  "place_external_ids": [4, 20684]
}
```

---

### 4. Update Project

**PATCH** `/projects/{id}`

**Path Parameters:**
- `id` (integer): Project ID

**Request Body:**
```json
{
  "name": "Updated Project Name",
  "description": "Updated description",
  "start_date": "2026-03-15"
}
```

**Request Body Fields (all optional):**
- `name` (string): Project name (1-255 characters)
- `description` (string): Project description
- `start_date` (string): Start date in format "YYYY-MM-DD"

**Success Response (200):**
```json
{
  "id": 1,
  "name": "Updated Project Name",
  "description": "Updated description",
  "start_date": "2026-03-15",
  "status": "active",
  "created_at": "2026-02-20T14:00:00",
  "updated_at": "2026-02-20T15:30:00",
  "places": []
}
```

**Error Response (404):**
```json
{
  "detail": "Project not found"
}
```

**Example:**
```bash
PATCH /api/v1/projects/1
Content-Type: application/json

{
  "name": "Updated Project Name"
}
```

---

### 5. Delete Project

**DELETE** `/projects/{id}`

**Path Parameters:**
- `id` (integer): Project ID

**Success Response (204):**
No content

**Error Response (400):**
```json
{
  "detail": "Cannot delete project with visited places"
}
```

**Error Response (404):**
```json
{
  "detail": "Project not found"
}
```

**Business Rule:**
Cannot delete a project if any of its places are marked as visited.

**Example:**
```bash
DELETE /api/v1/projects/1
```

---

## Project Places Endpoints

### 6. List Places in Project

**GET** `/projects/{project_id}/places/`

**Path Parameters:**
- `project_id` (integer): Project ID

**Success Response (200):**
```json
[
  {
    "id": 1,
    "project_id": 1,
    "external_id": 4,
    "title": "Priest and Boy",
    "artist_display": "Lawrence Carmichael Earle\nAmerican, 1845-1921",
    "image_url": "https://www.artic.edu/iiif/2/1753b638-d4fb-8e45-3db9-92dde7f053da/full/max/0/default.jpg",
    "notes": "Beautiful artwork!",
    "is_visited": true,
    "created_at": "2026-02-20T14:00:00",
    "updated_at": "2026-02-20T15:00:00"
  }
]
```

**Error Response (404):**
```json
{
  "detail": "Project not found"
}
```

**Example:**
```bash
GET /api/v1/projects/1/places/
```

---

### 7. Get Single Place

**GET** `/projects/{project_id}/places/{place_id}`

**Path Parameters:**
- `project_id` (integer): Project ID
- `place_id` (integer): Place ID

**Success Response (200):**
```json
{
  "id": 1,
  "project_id": 1,
  "external_id": 4,
  "title": "Priest and Boy",
  "artist_display": "Lawrence Carmichael Earle\nAmerican, 1845-1921",
  "image_url": "https://www.artic.edu/iiif/2/1753b638-d4fb-8e45-3db9-92dde7f053da/full/max/0/default.jpg",
  "notes": "Beautiful artwork!",
  "is_visited": true,
  "created_at": "2026-02-20T14:00:00",
  "updated_at": "2026-02-20T15:00:00"
}
```

**Error Response (404):**
```json
{
  "detail": "Place not found in this project"
}
```

**Example:**
```bash
GET /api/v1/projects/1/places/1
```

---

### 8. Add Place to Project

**POST** `/projects/{project_id}/places/`

**Path Parameters:**
- `project_id` (integer): Project ID

**Request Body:**
```json
{
  "external_id": 27992
}
```

**Request Body Fields:**
- `external_id` (integer, required): Artwork ID from Art Institute API (must be positive)

**Success Response (201):**
```json
{
  "id": 2,
  "project_id": 1,
  "external_id": 27992,
  "title": "A Sunday on La Grande Jatte — 1884",
  "artist_display": "Georges Seurat\nFrench, 1859-1891",
  "image_url": "https://www.artic.edu/iiif/2/2d484387-2509-5e8e-2c43-22f9981972eb/full/max/0/default.jpg",
  "notes": null,
  "is_visited": false,
  "created_at": "2026-02-20T15:00:00",
  "updated_at": "2026-02-20T15:00:00"
}
```

**Error Response (400):**
```json
{
  "detail": "Cannot add more than 10 places to a project"
}
```

```json
{
  "detail": "Place with external_id 27992 already exists in this project"
}
```

```json
{
  "detail": "Artwork 99999 not found in Art Institute API"
}
```

**Validation Rules:**
- Maximum 10 places per project
- external_id must be a positive integer
- external_id must be unique within the project
- Artwork must exist in Art Institute API

**Example:**
```bash
POST /api/v1/projects/1/places/
Content-Type: application/json

{
  "external_id": 27992
}
```

---

### 9. Update Place

**PATCH** `/projects/{project_id}/places/{place_id}`

**Path Parameters:**
- `project_id` (integer): Project ID
- `place_id` (integer): Place ID

**Request Body:**
```json
{
  "notes": "Amazing painting! Must see again.",
  "is_visited": true
}
```

**Request Body Fields (all optional):**
- `notes` (string): Personal notes about the place
- `is_visited` (boolean): Whether the place has been visited

**Success Response (200):**
```json
{
  "id": 1,
  "project_id": 1,
  "external_id": 4,
  "title": "Priest and Boy",
  "artist_display": "Lawrence Carmichael Earle\nAmerican, 1845-1921",
  "image_url": "https://www.artic.edu/iiif/2/1753b638-d4fb-8e45-3db9-92dde7f053da/full/max/0/default.jpg",
  "notes": "Amazing painting! Must see again.",
  "is_visited": true,
  "created_at": "2026-02-20T14:00:00",
  "updated_at": "2026-02-20T16:00:00"
}
```

**Error Response (404):**
```json
{
  "detail": "Place not found in this project"
}
```

**Business Logic:**
When all places in a project are marked as `is_visited: true`, the project status automatically changes to `"completed"`.

**Example:**
```bash
PATCH /api/v1/projects/1/places/1
Content-Type: application/json

{
  "notes": "Beautiful artwork!",
  "is_visited": true
}
```

---

## Data Models

### Project

```typescript
{
  id: number;
  name: string;
  description: string | null;
  start_date: string | null;  // Format: "YYYY-MM-DD"
  status: "active" | "completed";
  created_at: string;  // ISO 8601 format
  updated_at: string;  // ISO 8601 format
  places: Place[];
}
```

### Place

```typescript
{
  id: number;
  project_id: number;
  external_id: number;
  title: string;
  artist_display: string | null;
  image_url: string | null;
  notes: string | null;
  is_visited: boolean;
  created_at: string;  // ISO 8601 format
  updated_at: string;  // ISO 8601 format
}
```

---

## Business Rules Summary

1. **Project Limits:**
   - Minimum 1 place per project (can be added after creation)
   - Maximum 10 places per project

2. **Project Status:**
   - `"active"` - Default status when created
   - `"completed"` - Automatically set when all places are visited

3. **Place Uniqueness:**
   - Cannot add the same `external_id` to a project twice

4. **Delete Protection:**
   - Cannot delete a project if any place is marked as visited

5. **API Validation:**
   - All `external_id` values must exist in Art Institute API
   - All `external_id` values must be positive integers

---

## Example Art Institute API IDs

Valid artwork IDs for testing:
- `4` - Priest and Boy
- `20684` - Paris Street; Rainy Day
- `27992` - A Sunday on La Grande Jatte — 1884
- `28560` - The Bedroom
- `16487` - The Basket of Apples

---

## CORS Configuration

The API is configured to accept requests from all origins during development.

Allowed methods: GET, POST, PATCH, DELETE
Allowed headers: Content-Type, Authorization

---

## Interactive Documentation

For testing and exploring the API interactively:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Error Handling

The API uses standard HTTP status codes and returns error details in the response body.

Common error scenarios:

1. **Validation Error (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

2. **Business Logic Error (400):**
```json
{
  "detail": "Cannot add more than 10 places to a project"
}
```

3. **Not Found (404):**
```json
{
  "detail": "Project not found"
}
```

---

## Frontend Integration Tips

1. **Project Status Badge:**
   - Show "Active" badge for `status === "active"`
   - Show "Completed" badge for `status === "completed"`

2. **Image Display:**
   - All `image_url` values are ready to use in `<img>` tags
   - Use `image_url || '/placeholder.jpg'` for fallback

3. **Date Formatting:**
   - `start_date` is in "YYYY-MM-DD" format
   - `created_at` and `updated_at` are in ISO 8601 format

4. **Visited Places Counter:**
   - Calculate: `places.filter(p => p.is_visited).length` / `places.length`

5. **Form Validation:**
   - Project name: required, 1-255 characters
   - Places: 0-10 items
   - external_id: positive integer

---

## Rate Limiting

Art Institute API has rate limiting:
- 60 requests per minute per IP (anonymous)
- The backend handles API requests, so frontend doesn't need to worry about this

---

## Development Server

Start the backend server:
```bash
docker compose up
```

The API will be available at: `http://localhost:8000`
