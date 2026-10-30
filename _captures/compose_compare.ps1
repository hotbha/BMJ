Add-Type -AssemblyName System.Drawing

$pairs = @(
    @{ Name = '01_home';         Label = 'HOME DASHBOARD' },
    @{ Name = '02_pdp';          Label = 'PRODUCT DETAIL' },
    @{ Name = '03_cart';         Label = 'CART SUMMARY' },
    @{ Name = '04_subscription'; Label = 'SUBSCRIPTION DASHBOARD' }
)

$gap = 24
$bar = 70

foreach ($p in $pairs) {
    $before = [System.Drawing.Image]::FromFile("X:\BMJ\_captures\before\$($p.Name).png")
    $after  = [System.Drawing.Image]::FromFile("X:\BMJ\_captures\after\$($p.Name).png")

    $w = $before.Width + $gap + $after.Width
    $h = $bar + [Math]::Max($before.Height, $after.Height)
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.Clear([System.Drawing.Color]::FromArgb(24, 20, 18))
    $g.InterpolationMode = 'HighQualityBicubic'
    $g.TextRenderingHint = 'AntiAliasGridFit'

    $g.DrawImage($before, (New-Object System.Drawing.Rectangle(0, $bar, $before.Width, $before.Height)))
    $g.DrawImage($after, (New-Object System.Drawing.Rectangle(($before.Width + $gap), $bar, $after.Width, $after.Height)))

    $font = New-Object System.Drawing.Font('Segoe UI', 22, [System.Drawing.FontStyle]::Bold)
    $small = New-Object System.Drawing.Font('Segoe UI', 18)
    $brush = [System.Drawing.Brushes]::White
    $dim = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(190, 160, 140))
    $g.DrawString("BEFORE  |  $($p.Label)", $font, $brush, 24, 16)
    $g.DrawString('HEAD e1d11e6 (legacy UI)  vs  working tree (vibrant_zest)', $small, $dim, 24, 46)
    $g.DrawString('AFTER  |  430x932-equivalent golden render', $small, $dim, ($before.Width + $gap + 24), 46)

    $out = "X:\BMJ\_captures\compare\$($p.Name)_before_after.png"
    New-Item -ItemType Directory -Force -Path 'X:\BMJ\_captures\compare' | Out-Null
    $bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)

    $g.Dispose(); $bmp.Dispose(); $before.Dispose(); $after.Dispose()
    Write-Output "wrote $out"
}
