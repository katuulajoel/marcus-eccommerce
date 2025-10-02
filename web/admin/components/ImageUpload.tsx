import { useCallback, useState } from "react"
import { Upload, X, Image as ImageIcon } from "lucide-react"
import { Button } from "@shared/components/ui/button"
import { Label } from "@shared/components/ui/label"

interface ImageUploadProps {
  label?: string
  currentImageUrl?: string | null
  onImageChange: (file: File | null) => void
  onImageClear?: () => void
  error?: string
  accept?: string
  maxSizeMB?: number
}

export function ImageUpload({
  label = "Image",
  currentImageUrl,
  onImageChange,
  onImageClear,
  error,
  accept = "image/jpeg,image/png,image/webp",
  maxSizeMB = 5,
}: ImageUploadProps) {
  const [preview, setPreview] = useState<string | null>(null)
  const [dragActive, setDragActive] = useState(false)

  const handleFile = useCallback(
    (file: File | null) => {
      if (!file) {
        setPreview(null)
        onImageChange(null)
        return
      }

      // Validate file size
      const maxSizeBytes = maxSizeMB * 1024 * 1024
      if (file.size > maxSizeBytes) {
        alert(`File size must be less than ${maxSizeMB}MB`)
        return
      }

      // Validate file type
      if (!file.type.startsWith("image/")) {
        alert("Please upload an image file")
        return
      }

      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(file)

      onImageChange(file)
    },
    [maxSizeMB, onImageChange]
  )

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null
    handleFile(file)
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const file = e.dataTransfer.files?.[0] || null
    handleFile(file)
  }

  const handleClear = () => {
    setPreview(null)
    onImageChange(null)
    if (onImageClear) {
      onImageClear()
    }
  }

  const displayImage = preview || currentImageUrl

  return (
    <div className="grid gap-2">
      <Label htmlFor="image-upload">{label}</Label>

      {displayImage ? (
        <div className="relative">
          <img
            src={displayImage}
            alt="Preview"
            className="w-full max-w-sm h-48 object-cover rounded-md border"
          />
          <Button
            type="button"
            variant="destructive"
            size="icon"
            className="absolute top-2 right-2"
            onClick={handleClear}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      ) : (
        <div
          className={`border-2 border-dashed rounded-md p-8 text-center transition-colors ${
            dragActive
              ? "border-primary bg-primary/5"
              : "border-muted-foreground/25 hover:border-primary/50"
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            id="image-upload"
            type="file"
            accept={accept}
            onChange={handleFileChange}
            className="hidden"
          />
          <label
            htmlFor="image-upload"
            className="cursor-pointer flex flex-col items-center gap-2"
          >
            <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
              <Upload className="h-6 w-6 text-primary" />
            </div>
            <div className="text-sm">
              <span className="font-medium text-primary">Click to upload</span> or drag and drop
            </div>
            <div className="text-xs text-muted-foreground">
              PNG, JPG, WebP up to {maxSizeMB}MB
            </div>
          </label>
        </div>
      )}

      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  )
}
