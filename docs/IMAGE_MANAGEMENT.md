# Image Management System

This document explains how the image management system works in the Marcus Custom Bikes e-commerce platform.

## Overview

The platform uses Django's `ImageField` for managing product images with automatic cleanup, cloud storage support, and a user-friendly upload interface in the admin panel.

## Features

- ✅ **File Upload**: Drag-and-drop or click to upload images
- ✅ **Image Preview**: Live preview before and after upload
- ✅ **Automatic Cleanup**: Old images are automatically deleted when replaced or when models are deleted
- ✅ **Cloud Storage**: Production-ready S3/CloudFront CDN integration
- ✅ **Validation**: Client and server-side validation for file size and type
- ✅ **Thumbnails**: Display thumbnails in admin tables

## Models with Image Support

### 1. Category
- **Field**: `image` (ImageField)
- **Upload Path**: `categories/`
- **Use Case**: Category banner/icon images

### 2. PartOption
- **Field**: `image` (ImageField)
- **Upload Path**: `part_options/`
- **Use Case**: Images of individual bike parts (frames, wheels, etc.)

### 3. PreConfiguredProduct
- **Field**: `image` (ImageField)
- **Upload Path**: `preconfigured_products/`
- **Use Case**: Product showcase images for pre-configured bikes

## Backend Setup

### Development (Local Filesystem)

By default, images are stored in `server/media/` directory:

```
server/
├── media/
│   ├── categories/
│   ├── part_options/
│   └── preconfigured_products/
```

### Production (AWS S3 + CloudFront)

Configure the following environment variables:

```bash
USE_S3=True
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=us-east-1  # Optional, defaults to us-east-1
```

## Image Cleanup

Images are automatically deleted in the following scenarios:

### 1. On Model Update
When a model's image is replaced with a new one, the old image file is automatically deleted.

**Implementation**: `pre_save` signal in `apps/*/signals.py`

### 2. On Model Deletion
When a model is deleted, its associated image is automatically deleted.

**Implementation**: `post_delete` signal in `apps/*/signals.py`

### 3. Orphaned Images
Images that exist in storage but aren't referenced by any model can be identified and cleaned up.

**Implementation**: Run the cleanup script (coming soon)

## Admin Interface Usage

### Uploading Images

1. **Categories Page**
   - Navigate to Categories
   - Click "Add Category" or "Edit" on existing category
   - Use the image upload component:
     - Drag and drop an image
     - OR click to browse and select a file
   - Preview appears immediately
   - Save the category

2. **Part Options Page**
   - Similar to categories
   - Upload images for each part option

3. **Preconfigured Products Page**
   - Navigate through the configurator
   - At the final step, upload a product image
   - Image appears in the product table after creation

### Image Preview

- **Tables**: Thumbnails (48x48px) are displayed in the first column
- **Forms**: Full preview shown before submission
- **Clearing**: Click the X button on a preview to clear/remove the image

## File Validation

### Client-Side (Frontend)
- **Max Size**: 5MB (configurable)
- **Formats**: JPEG, PNG, WebP
- **User Feedback**: Alerts for invalid files

### Server-Side (Backend)
- **Pillow Library**: Validates actual image data
- **Size Limits**: Enforced by Django settings
- **Format Check**: Only image/* MIME types accepted

## API Usage

### Creating with Image

```typescript
// Example: Creating a category with an image
const formData = new FormData();
formData.append('name', 'Bikes');
formData.append('description', 'High-quality bikes');
formData.append('image', imageFile);  // File object
formData.append('is_active', 'true');

await fetch('/api/categories/', {
  method: 'POST',
  body: formData,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});
```

### Updating an Image

```typescript
// Example: Updating just the image
const formData = new FormData();
formData.append('image', newImageFile);

await fetch('/api/categories/1/', {
  method: 'PATCH',
  body: formData,
});
```

### Clearing an Image

```typescript
// Set image to empty string to clear
const formData = new FormData();
formData.append('image', '');

await fetch('/api/categories/1/', {
  method: 'PATCH',
  body: formData,
});
```

## Migration from image_url

If you have existing data using `image_url` CharField:

### 1. Manual Upload (if needed)

For external URLs, download images and upload them through the admin interface.

### 2. Remove old fields

After confirming all images are migrated:

```bash
# Remove image_url fields from models
# Then generate migrations
python manage.py makemigrations
python manage.py migrate
```

## Storage Configuration

### Local Development

No configuration needed. Images stored in `server/media/`.

### Production (S3)

1. Create an S3 bucket
2. Configure CORS on the bucket
3. Set environment variables
4. Images are automatically uploaded to S3
5. URLs use CloudFront CDN (if configured)

### Example S3 CORS Configuration

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": []
  }
]
```

## Troubleshooting

### Images not displaying

1. **Check file exists**: Look in `server/media/` directory
2. **Check permissions**: Ensure media directory is readable
3. **Check URL**: Verify MEDIA_URL is configured correctly
4. **Check serializer**: Ensure `image_url` field is in serializer

### Upload fails

1. **File too large**: Check max size (default 5MB)
2. **Invalid format**: Ensure file is JPEG/PNG/WebP
3. **Permissions**: Check write permissions on media directory
4. **Pillow not installed**: Run `pip install Pillow`

### Images not deleted

1. **Signals not registered**: Check `apps.py` imports signals
2. **File permissions**: Ensure delete permissions on media directory

## Best Practices

1. **Optimize images before upload**: Compress and resize to appropriate dimensions
2. **Use descriptive filenames**: Helps with organization and SEO
3. **Regular cleanup**: Periodically check for orphaned images
4. **Backup strategy**: Include media files in backup plans
5. **CDN in production**: Always use CloudFront or similar CDN for performance

## Future Enhancements

- [ ] Automatic image optimization (resize, compress)
- [ ] Multiple image sizes (thumbnail, medium, full)
- [ ] WebP conversion for modern browsers
- [ ] Bulk image upload
- [ ] Image gallery for products
- [ ] Scheduled cleanup of orphaned images
