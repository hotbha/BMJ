<#
    V1-cleanup evidence helper (audit tooling, NOT part of the product).

    For each candidate name in -Names, counts every NON-SELF reference found under
    -Root and writes:
        <name>|<hit count>|<hit paths>          (or)
        <name>|0|NO-REFS-OUTSIDE-SELF

    A row is only usable as "proof of no references" when it reports
    0 hits AND the file is not a build/tooling input.

    Usage:
      powershell -NoProfile -File _cleanup_refcheck.ps1 `
        -Root x:\BMJ -Names x:\BMJ\_cleanup_names_root.txt -Out x:\BMJ\_cleanup_refs_root.txt
#>
param(
    [Parameter(Mandatory = $true)][string]$Root,
    [Parameter(Mandatory = $true)][string]$Names,
    [Parameter(Mandatory = $true)][string]$Out,
    [switch]$IgnoreCase
)

# Exclude dependency/build trees so hits are real source references.
$globExcludes = @(
    '--glob', '!**/node_modules/**',
    '--glob', '!**/.git/**',
    '--glob', '!**/.venv/**',
    '--glob', '!**/.venv-1/**',
    '--glob', '!**/.pytest_cache/**',
    '--glob', '!**/target/**',
    '--glob', '!**/build/**',
    '--glob', '!**/.dart_tool/**',
    '--glob', '!**/Stitch/**',
    '--glob', '!**/*.log',
    '--glob', '!**/.gradle/**',
    '--glob', '!**/.kotlin/**',
    '--glob', '!**/.idea/**',
    '--glob', '!**/Pods/**',
    '--glob', '!**/_cleanup_*'
)

$lines = Get-Content -LiteralPath $Names | Where-Object { $_.Trim().Length -gt 0 }
$results = New-Object System.Collections.Generic.List[string]

foreach ($line in $lines) {
    $n = $line.Trim()
    $rgArgs = @('-F', '-l', '--no-ignore', '--hidden') + $globExcludes
    if ($IgnoreCase) { $rgArgs += '--ignore-case' }
    $rgArgs += @('-e', $n, $Root)
    $hits = & rg @rgArgs 2>$null
    $hits = @($hits | Where-Object {
        if (-not $_) { return $false }
        $leaf = [System.IO.Path]::GetFileName($_)
        $stem = [System.IO.Path]::GetFileNameWithoutExtension($_)
        return ($leaf -ne $n) -and ($stem -ne $n)
    })
    if ($hits.Count -gt 0) {
        $shown = $hits | Select-Object -First 6
        $suffix = if ($hits.Count -gt 6) { ' ; ...' } else { '' }
        $results.Add(("{0}|{1}|{2}{3}" -f $n, $hits.Count, ($shown -join ' ; '), $suffix))
    }
    else {
        $results.Add(("{0}|0|NO-REFS-OUTSIDE-SELF" -f $n))
    }
}

$results | Set-Content -LiteralPath $Out -Encoding UTF8
Write-Output ("rows={0} -> {1}" -f $results.Count, $Out)
