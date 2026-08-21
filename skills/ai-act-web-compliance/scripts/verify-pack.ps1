[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$skillRoot = Split-Path -Parent $PSScriptRoot
$checksumFile = Join-Path $skillRoot 'assets\eu-icons\SHA256SUMS.txt'
$iconRoot = Join-Path $skillRoot 'assets\eu-icons'
$requiredFiles = @(
    'SKILL.md',
    'agents\openai.yaml',
    'references\legal-preflight.md',
    'references\decision-tree.md',
    'references\generation-workflow.md',
    'references\icons-and-labels.md',
    'references\web-implementation.md',
    'references\enforcement-and-evidence.md',
    'references\official-sources.md',
    'assets\eu-icons\SOURCE.md',
    'assets\web\ai-disclosure.css',
    'assets\web\examples.html',
    'scripts\verify-preflight-yaml.py'
)

$errors = [System.Collections.Generic.List[string]]::new()

foreach ($relativePath in $requiredFiles) {
    $absolutePath = Join-Path $skillRoot $relativePath
    if (-not (Test-Path -LiteralPath $absolutePath -PathType Leaf)) {
        $errors.Add("Missing required file: $relativePath")
    }
}

$generatedArtifacts = Get-ChildItem -LiteralPath $skillRoot -Recurse -Force |
    Where-Object {
        $_.Name -in '__pycache__', '.pytest_cache', '.DS_Store', 'Thumbs.db' -or
        $_.Extension -in '.pyc', '.pyo'
    }
foreach ($artifact in $generatedArtifacts) {
    $relativeArtifact = $artifact.FullName.Substring($skillRoot.Length).TrimStart(
        [char[]]'\/'
    )
    $errors.Add("Forbidden generated artifact: $relativeArtifact")
}

$authoredTextExtensions = '.css', '.html', '.md', '.ps1', '.py', '.txt',
    '.yaml', '.yml'
$authoredTextFiles = Get-ChildItem -LiteralPath $skillRoot -Recurse -File |
    Where-Object { $_.Extension -in $authoredTextExtensions }
foreach ($textFile in $authoredTextFiles) {
    $bytes = [System.IO.File]::ReadAllBytes($textFile.FullName)
    if ($bytes -contains 13) {
        $relativeText = $textFile.FullName.Substring($skillRoot.Length).TrimStart(
            [char[]]'\/'
        )
        $errors.Add("Authored text must use LF line endings: $relativeText")
    }
}

$manifestIconPaths = [System.Collections.Generic.HashSet[string]]::new(
    [System.StringComparer]::OrdinalIgnoreCase
)
if (-not (Test-Path -LiteralPath $checksumFile -PathType Leaf)) {
    $errors.Add('Missing icon checksum manifest.')
}
else {
    $checksumLines = Get-Content -LiteralPath $checksumFile |
        Where-Object { $_.Trim().Length -gt 0 }

    if ($checksumLines.Count -ne 24) {
        $errors.Add("Expected 24 icon checksums, found $($checksumLines.Count).")
    }

    foreach ($line in $checksumLines) {
        if ($line -notmatch '^(?<hash>[0-9a-f]{64})  (?<path>.+)$') {
            $errors.Add("Invalid checksum line: $line")
            continue
        }

        $relativeIconPath = $Matches.path.Replace(
            '/',
            [System.IO.Path]::DirectorySeparatorChar
        )
        if ([System.IO.Path]::IsPathRooted($relativeIconPath)) {
            $errors.Add("Icon checksum path must be relative: $relativeIconPath")
            continue
        }
        if ($relativeIconPath.Split([char[]]'\/') -contains '..') {
            $errors.Add("Icon checksum path escapes asset root: $relativeIconPath")
            continue
        }

        $iconPath = [System.IO.Path]::GetFullPath(
            (Join-Path $iconRoot $relativeIconPath)
        )
        $relativeToIconRoot = [System.IO.Path]::GetRelativePath(
            $iconRoot,
            $iconPath
        )
        $firstIconSegment = $relativeToIconRoot.Split([char[]]'\/')[0]
        if (
            [System.IO.Path]::IsPathRooted($relativeToIconRoot) -or
            $firstIconSegment -eq '..'
        ) {
            $errors.Add("Icon checksum path escapes asset root: $relativeIconPath")
            continue
        }

        $manifestPath = $relativeToIconRoot.Replace(
            [System.IO.Path]::DirectorySeparatorChar,
            '/'
        )
        if (-not $manifestIconPaths.Add($manifestPath)) {
            $errors.Add("Duplicate icon checksum path: $manifestPath")
            continue
        }
        if (-not (Test-Path -LiteralPath $iconPath -PathType Leaf)) {
            $errors.Add("Missing icon: $relativeIconPath")
            continue
        }

        $fileHash = Get-FileHash -Algorithm SHA256 -LiteralPath $iconPath
        $actualHash = $fileHash.Hash.ToLowerInvariant()
        if ($actualHash -ne $Matches.hash) {
            $errors.Add("Checksum mismatch: $relativeIconPath")
        }
    }
}

$iconFiles = Get-ChildItem -LiteralPath $iconRoot `
    -Recurse -File | Where-Object { $_.Extension -in '.svg', '.png' }
if ($iconFiles.Count -ne 24) {
    $errors.Add("Expected 24 icon files, found $($iconFiles.Count).")
}

$actualIconPaths = [System.Collections.Generic.HashSet[string]]::new(
    [System.StringComparer]::OrdinalIgnoreCase
)
foreach ($iconFile in $iconFiles) {
    $relativeIcon = [System.IO.Path]::GetRelativePath(
        $iconRoot,
        $iconFile.FullName
    ).Replace([System.IO.Path]::DirectorySeparatorChar, '/')
    $null = $actualIconPaths.Add($relativeIcon)
    if (-not $manifestIconPaths.Contains($relativeIcon)) {
        $errors.Add("Missing icon checksum entry: $relativeIcon")
    }
}
foreach ($manifestIconPath in $manifestIconPaths) {
    if (-not $actualIconPaths.Contains($manifestIconPath)) {
        $errors.Add("Checksum entry has no bundled icon: $manifestIconPath")
    }
}

$skillText = Get-Content -Raw -LiteralPath (Join-Path $skillRoot 'SKILL.md')
$requiredSkillText = @(
    'Always perform a live official-source preflight',
    'The EU icons are optional',
    'Stop each definitive legal conclusion whose controlling source cannot be',
    'do not suppress a separately supported EU-law conclusion',
    'Prefix every material wording, timing, placement, repetition, and persistence',
    "the Code's audio-at-the-beginning implementation",
    'Use only the exact official URL that was opened during the current preflight',
    'Before returning, open or otherwise verify every cited URL',
    'shorten, or guess a citation path',
    'End every legal or compliance answer with the complete `Preflight record` YAML',
    'a prose summary does not replace it',
    'parse the final fenced block as YAML',
    'with no stray delimiter',
    'Never headline or summarize an assessment as `PASS`, `compliant`',
    'State the narrower Article 50 classification',
    'perform an adversarial self-check',
    'Test one expected path and one forbidden or failure path',
    'A string-presence assertion'
)
foreach ($requiredText in $requiredSkillText) {
    if (-not $skillText.Contains($requiredText)) {
        $errors.Add("Missing fail-closed skill contract: $requiredText")
    }
}

$contentContracts = @(
    @{
        Path = 'references\legal-preflight.md'
        Required = @(
            'This is a fail-closed gate',
            'checked_at: YYYY-MM-DDTHH:MM:SS+TZ',
            'national_sources:',
            'the named successor and record both process identifiers',
            'An HTTP success',
            'map the gap to the conclusions it could change',
            'do not use it to block an independently supported'
        )
    },
    @{
        Path = 'references\decision-tree.md'
        Required = @(
            '## 0. Fix the relevant date',
            '2 December 2026',
            'do not need retroactive marking or',
            'It does not postpone Article 50(1)',
            'source code and integral code comments or configuration',
            'machine-to-machine',
            'closed-loop industrial or product-',
            '**Deepfake criminal-law exception:**',
            '**Public-interest-text criminal-law exception:**'
        )
    },
    @{
        Path = 'references\generation-workflow.md'
        Required = @(
            '## Before generation',
            '## During generation',
            '## After generation',
            '**LAW, chatbot/agent:**',
            '**CODE, audio-only:**',
            'Do not ask a tool or pipeline to remove a watermark'
        )
    },
    @{
        Path = 'references\icons-and-labels.md'
        Required = @(
            'The icon is optional',
            'official-looking audio mark',
            'Fully AI-generated',
            'Partially AI-modified',
            'Basic AI',
            'A law-enforcement context alone',
            'does not establish that exception'
        )
    },
    @{
        Path = 'references\web-implementation.md'
        Required = @(
            '**CODE implementation:**',
            'include the audible disclaimer at the beginning',
            'Article 50(1) chatbot',
            'Never absolutely position a custom control',
            'fullscreen the labelled wrapper'
        )
    },
    @{
        Path = 'references\enforcement-and-evidence.md'
        Required = @(
            'Authorities do not need a universal `AI detector`',
            'EUR 15 million',
            'EUR 7.5 million'
        )
    },
    @{
        Path = 'references\official-sources.md'
        Required = @(
            'Baseline observed on 21 August 2026',
            'Article 50 overview',
            '5 August 2026',
            'Official document ID',
            '`131215`',
            '`129555`',
            '30861FC5DE31205846F023068069C92FABC7271EBEAC6AF7BEF68B97F0A33F66',
            '7BD22C5A3C56EAEFDA27A5BF7A6118198EF2A9C9255241BD97ABF7CDEDF9BC28'
        )
    }
)

foreach ($contract in $contentContracts) {
    $contractPath = Join-Path $skillRoot $contract.Path
    if (-not (Test-Path -LiteralPath $contractPath -PathType Leaf)) {
        continue
    }

    $contractText = Get-Content -Raw -LiteralPath $contractPath
    foreach ($requiredText in $contract.Required) {
        if (-not $contractText.Contains($requiredText)) {
            $errors.Add("Missing content contract in $($contract.Path): $requiredText")
        }
    }
}

$preflightPath = Join-Path $skillRoot 'references\legal-preflight.md'
if (Test-Path -LiteralPath $preflightPath -PathType Leaf) {
    $preflightText = Get-Content -Raw -LiteralPath $preflightPath
    $yamlBlocks = [regex]::Matches(
        $preflightText,
        '(?ms)^```yaml[ \t]*\r?\n(?<body>.*?)^```[ \t]*$'
    )
    if ($yamlBlocks.Count -ne 1) {
        $errors.Add(
            "Expected one preflight YAML block, found $($yamlBlocks.Count)."
        )
    }
    else {
        $yamlValidator = Join-Path $PSScriptRoot 'verify-preflight-yaml.py'
        $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
        if ($null -eq $pythonCommand) {
            $errors.Add('Python with PyYAML is required to validate preflight YAML.')
        }
        elseif (Test-Path -LiteralPath $yamlValidator -PathType Leaf) {
            $yamlValidationOutput = $yamlBlocks[0].Groups['body'].Value |
                & $pythonCommand.Source $yamlValidator --template 2>&1
            if ($LASTEXITCODE -ne 0) {
                $errors.Add(
                    'Preflight YAML schema validation failed: ' +
                    ($yamlValidationOutput -join ' ')
                )
            }
        }
    }
}

$examplePath = Join-Path $skillRoot 'assets\web\examples.html'
if (Test-Path -LiteralPath $examplePath -PathType Leaf) {
    $exampleHtml = Get-Content -Raw -LiteralPath $examplePath
    $assetMatches = [regex]::Matches(
        $exampleHtml,
        '(?:src|href)="(?<path>[^"#]+)"'
    )
    foreach ($assetMatch in $assetMatches) {
        $assetReference = $assetMatch.Groups['path'].Value
        if ($assetReference -match '^(?:https?:|data:|mailto:)') {
            continue
        }

        $normalisedReference = $assetReference.Replace('/', '\')
        $resolvedAsset = [System.IO.Path]::GetFullPath(
            (Join-Path (Split-Path -Parent $examplePath) $normalisedReference)
        )
        $relativeToSkill = [System.IO.Path]::GetRelativePath(
            $skillRoot,
            $resolvedAsset
        )
        $firstAssetSegment = $relativeToSkill.Split([char[]]'\/')[0]
        if (
            [System.IO.Path]::IsPathRooted($relativeToSkill) -or
            $firstAssetSegment -eq '..'
        ) {
            $errors.Add("Local example asset escapes skill root: $assetReference")
            continue
        }
        if (-not (Test-Path -LiteralPath $resolvedAsset -PathType Leaf)) {
            $errors.Add("Broken local example asset: $assetReference")
        }
    }
}

if ($errors.Count -gt 0) {
    Write-Error ($errors -join [Environment]::NewLine)
    exit 1
}

Write-Output 'PASS: skill structure, parsed preflight schema, and all 24 official icon assets match.'
