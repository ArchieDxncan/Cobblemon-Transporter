# Simple-Scale-PngImages.ps1
# Simple script to scale all PNG images in the current directory and subfolders by 2x

# Add required assembly
Add-Type -AssemblyName System.Drawing

# Function to scale an image
function Resize-Image {
    param (
        [Parameter(Mandatory=$true)]
        [string]$InputFile
    )
    
    Write-Host "Processing: $InputFile"
    
    try {
        # Load image
        $img = [System.Drawing.Image]::FromFile($InputFile)
        
        # Calculate new dimensions (2x scale)
        $newWidth = $img.Width * 2
        $newHeight = $img.Height * 2
        
        # Create new bitmap
        $bmp = New-Object System.Drawing.Bitmap($newWidth, $newHeight)
        
        # Create graphics object
        $graphics = [System.Drawing.Graphics]::FromImage($bmp)
        $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
        
        # Draw the image
        $graphics.DrawImage($img, 0, 0, $newWidth, $newHeight)
        
        # Save the image (close the original file first)
        $img.Dispose()
        $bmp.Save($InputFile, [System.Drawing.Imaging.ImageFormat]::Png)
        
        # Clean up
        $graphics.Dispose()
        $bmp.Dispose()
        
        Write-Host "Successfully scaled: $InputFile"
    }
    catch {
        Write-Host "Error processing $InputFile`: $_" -ForegroundColor Red
    }
    finally {
        # Make sure everything is disposed
        if ($graphics) { $graphics.Dispose() }
        if ($bmp) { $bmp.Dispose() }
        if ($img) { $img.Dispose() }
    }
}

# Find all PNG files in the current directory and its subdirectories
Write-Host "Finding PNG files..."
$pngFiles = Get-ChildItem -Path . -Filter "*.png" -Recurse

# Process each file
$total = $pngFiles.Count
Write-Host "Found $total PNG files to process."

foreach ($file in $pngFiles) {
    Resize-Image -InputFile $file.FullName
}

Write-Host "Processing complete."