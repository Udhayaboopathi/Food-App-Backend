# Image Upload API

## Upload Single Image

```bash
curl -X POST "http://localhost:8000/upload/image" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@path/to/image.jpg"
```

Response:

```json
{
  "filename": "uuid-generated-name.jpg",
  "url": "/uploads/uuid-generated-name.jpg",
  "uploaded_at": "2025-12-06T10:30:00"
}
```

## Upload Multiple Images

```bash
curl -X POST "http://localhost:8000/upload/images" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@image1.jpg" \
  -F "files=@image2.png"
```

Response:

```json
{
  "count": 2,
  "files": [
    {
      "filename": "uuid-1.jpg",
      "url": "/uploads/uuid-1.jpg",
      "original_name": "image1.jpg"
    },
    {
      "filename": "uuid-2.png",
      "url": "/uploads/uuid-2.png",
      "original_name": "image2.png"
    }
  ],
  "uploaded_at": "2025-12-06T10:30:00"
}
```

## Delete Image

```bash
curl -X DELETE "http://localhost:8000/upload/image/uuid-filename.jpg" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Access Uploaded Images

Images are accessible at:

```
http://localhost:8000/uploads/filename.jpg
```

## Features

- ✅ Single & multiple image uploads
- ✅ UUID-based unique filenames
- ✅ File type validation (jpg, jpeg, png, gif, webp)
- ✅ Maximum file size: 5MB per image
- ✅ Maximum 10 files per batch upload
- ✅ Delete uploaded images
- ✅ Static file serving for uploaded images
- ✅ Automatic uploads directory creation

## File Storage

All images are stored in the `backend/uploads/` directory with unique UUID filenames to prevent conflicts.

## Using in Forms

When updating restaurants or menu items, upload the image first, then use the returned URL:

```javascript
// 1. Upload image
const formData = new FormData();
formData.append("file", imageFile);
const uploadResponse = await fetch("http://localhost:8000/upload/image", {
  method: "POST",
  body: formData,
  headers: { Authorization: `Bearer ${token}` },
});
const { url } = await uploadResponse.json();

// 2. Create/update restaurant with image URL
await fetch("http://localhost:8000/restaurants", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  },
  body: JSON.stringify({
    name: "My Restaurant",
    image_url: `http://localhost:8000${url}`,
    // ... other fields
  }),
});
```
