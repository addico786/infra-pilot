$ErrorActionPreference = "Stop"

$ProjectPath = "C:\Users\adnan\Desktop\test\infra-pilot\InfraPilot_Project_Presentation.pptx"
$DesktopPath = "C:\Users\adnan\Desktop\InfraPilot_Project_Presentation.pptx"

$ppLayoutBlank = 12
$ppSaveAsOpenXMLPresentation = 24
$msoTextOrientationHorizontal = 1
$msoShapeRectangle = 1
$msoShapeRoundedRectangle = 5
$msoTrue = -1
$msoFalse = 0

function Rgb($r, $g, $b) {
    return [int]($r + ($g * 256) + ($b * 65536))
}

$ColorBg = Rgb 7 8 12
$ColorBg2 = Rgb 11 13 18
$ColorCard = Rgb 17 24 39
$ColorCard2 = Rgb 15 23 42
$ColorText = Rgb 248 250 252
$ColorMuted = Rgb 168 179 199
$ColorAccent = Rgb 0 113 227
$ColorGreen = Rgb 52 211 153
$ColorOrange = Rgb 249 115 22
$ColorWhite = Rgb 255 255 255
$ColorBlack = Rgb 29 29 31
$ColorLightBg = Rgb 245 245 247
$ColorBorder = Rgb 210 210 215

function Add-Box($Slide, [double]$X, [double]$Y, [double]$W, [double]$H, [int]$Fill, [int]$Line, [bool]$Round = $false) {
    $shapeType = if ($Round) { $msoShapeRoundedRectangle } else { $msoShapeRectangle }
    $shape = $Slide.Shapes.AddShape($shapeType, $X, $Y, $W, $H)
    $shape.Fill.ForeColor.RGB = $Fill
    if ($Line -ge 0) {
        $shape.Line.ForeColor.RGB = $Line
        $shape.Line.Weight = 1
    } else {
        $shape.Line.Visible = $msoFalse
    }
    return $shape
}

function Add-Text($Slide, [double]$X, [double]$Y, [double]$W, [double]$H, [string]$Text, [int]$Size = 20, [int]$Color = $ColorText, [bool]$Bold = $false, [string]$Align = "left") {
    $shape = $Slide.Shapes.AddTextbox($msoTextOrientationHorizontal, $X, $Y, $W, $H)
    $shape.TextFrame.MarginLeft = 4
    $shape.TextFrame.MarginRight = 4
    $shape.TextFrame.MarginTop = 2
    $shape.TextFrame.MarginBottom = 2
    $shape.TextFrame.WordWrap = $msoTrue
    $range = $shape.TextFrame.TextRange
    $range.Text = $Text
    $range.Font.Name = "Aptos"
    $range.Font.Size = $Size
    $range.Font.Color.RGB = $Color
    $range.Font.Bold = if ($Bold) { $msoTrue } else { $msoFalse }
    if ($Align -eq "center") { $range.ParagraphFormat.Alignment = 2 }
    if ($Align -eq "right") { $range.ParagraphFormat.Alignment = 3 }
    return $shape
}

function Add-Bullets($Slide, [double]$X, [double]$Y, [double]$W, [double]$H, [string[]]$Items, [int]$Size = 18, [int]$Color = $ColorText) {
    $text = ($Items | ForEach-Object { "• $_" }) -join "`r"
    $shape = Add-Text $Slide $X $Y $W $H $text $Size $Color $false "left"
    $shape.TextFrame.TextRange.ParagraphFormat.SpaceAfter = 6
    return $shape
}

function Add-SlideTitle($Slide, [int]$No, [string]$Title, [string]$Subtitle = "") {
    Add-Box $Slide 0 0 960 540 $ColorBg -1 | Out-Null
    Add-Box $Slide 42 42 6 54 $ColorAccent -1 | Out-Null
    Add-Text $Slide 62 30 650 42 $Title 28 $ColorText $true | Out-Null
    if ($Subtitle.Length -gt 0) {
        Add-Text $Slide 64 68 690 25 $Subtitle 12 $ColorMuted | Out-Null
    }
    Add-Text $Slide 855 505 60 20 ("{0:D2}" -f $No) 10 $ColorMuted $false "right" | Out-Null
}

function Add-InfoCard($Slide, [double]$X, [double]$Y, [double]$W, [double]$H, [string]$Title, [string[]]$Items, [int]$AccentColor) {
    Add-Box $Slide $X $Y $W $H $ColorCard (Rgb 35 48 68) $true | Out-Null
    Add-Box $Slide $X $Y 5 $H $AccentColor -1 | Out-Null
    Add-Text $Slide ($X + 18) ($Y + 14) ($W - 32) 28 $Title 16 $ColorText $true | Out-Null
    Add-Bullets $Slide ($X + 20) ($Y + 54) ($W - 34) ($H - 65) $Items 11 $ColorMuted | Out-Null
}

function Add-FrontPage($Presentation) {
    $slide = $Presentation.Slides.Add(1, $ppLayoutBlank)
    Add-Box $slide 0 0 960 540 $ColorWhite -1 | Out-Null
    Add-Box $slide 55 48 850 3 $ColorAccent -1 | Out-Null
    Add-Text $slide 90 72 780 58 "INFRA PILOT" 34 $ColorBlack $true "center" | Out-Null
    Add-Text $slide 90 132 780 36 "AI-Powered Infrastructure Drift Detection & AutoFix" 18 $ColorAccent $true "center" | Out-Null
    Add-Text $slide 120 188 720 30 "MAJOR PROJECT / DISSERTATION REPORT PRESENTATION" 14 $ColorBlack $true "center" | Out-Null
    Add-Text $slide 180 242 600 62 "Submitted by`rAdnan`rEnrollment No.: [Your Enrollment Number]" 15 $ColorBlack $false "center" | Out-Null
    Add-Text $slide 170 320 620 54 "in partial fulfillment for the award of the degree of`rBachelor of Computer Applications (BCA)" 14 $ColorBlack $false "center" | Out-Null
    Add-Text $slide 180 392 600 44 "Under the supervision of`r[Supervisor Name]" 14 $ColorBlack $false "center" | Out-Null
    Add-Text $slide 115 462 730 42 "Department of Computer Science & Engineering`rSchool of Engineering Sciences & Technology, Jamia Hamdard, New Delhi - 110062" 12 $ColorBlack $false "center" | Out-Null
    Add-Text $slide 420 510 120 20 "2026" 13 $ColorBlack $true "center" | Out-Null
}

function Add-ContentSlide($Presentation, [int]$No, [string]$Title, [string]$Subtitle, [scriptblock]$Body) {
    $slide = $Presentation.Slides.Add($No, $ppLayoutBlank)
    Add-SlideTitle $slide $No $Title $Subtitle
    & $Body $slide
}

$powerPoint = New-Object -ComObject PowerPoint.Application
$powerPoint.Visible = $msoTrue
$presentation = $powerPoint.Presentations.Add()
$presentation.PageSetup.SlideWidth = 960
$presentation.PageSetup.SlideHeight = 540

Add-FrontPage $presentation

Add-ContentSlide $presentation 2 "Introduction" "Why infrastructure drift matters" {
    param($slide)
    Add-Text $slide 62 110 420 210 "Modern cloud systems are managed through Terraform and Kubernetes manifests.`r`rSmall configuration mistakes can introduce downtime, security exposure, and production drift.`r`rInfraPilot acts as an AI-assisted co-pilot for detecting, explaining, and fixing these risks." 18 $ColorText | Out-Null
    Add-Box $slide 540 115 315 68 $ColorAccent -1 $true | Out-Null
    Add-Text $slide 562 135 270 34 "Core Idea" 22 $ColorWhite $true "center" | Out-Null
    Add-InfoCard $slide 538 215 320 190 "InfraPilot Helps Teams" @("Analyze infrastructure as code", "Predict drift progression", "Generate fix suggestions", "Support local and cloud AI") $ColorGreen
}

Add-ContentSlide $presentation 3 "Problem Statement" "What teams struggle with today" {
    param($slide)
    Add-InfoCard $slide 58 118 258 318 "Manual Review" @("Slow and inconsistent", "Easy to miss risky defaults", "Depends heavily on expert availability") $ColorOrange
    Add-InfoCard $slide 351 118 258 318 "Configuration Drift" @("Cloud state changes over time", "IaC files become outdated", "Production behavior becomes unpredictable") $ColorAccent
    Add-InfoCard $slide 644 118 258 318 "Fix Handoff" @("Issues are detected but not fixed quickly", "Patch writing takes time", "Security risks stay open longer") $ColorGreen
}

Add-ContentSlide $presentation 4 "Project Objectives" "What InfraPilot is built to achieve" {
    param($slide)
    Add-Box $slide 75 115 810 335 $ColorCard (Rgb 35 48 68) $true | Out-Null
    Add-Bullets $slide 105 145 750 270 @(
        "Detect misconfigurations in Terraform and Kubernetes manifests.",
        "Calculate a simple drift score that summarizes infrastructure risk.",
        "Generate timeline-style predictions for how drift can evolve.",
        "Support multiple AI providers: Ollama, Gemini, and Oumi scoring.",
        "Provide rule-engine fallback so analysis still works when AI is unavailable.",
        "Offer AutoFix patch generation through the Cline workflow path."
    ) 18 $ColorText | Out-Null
}

Add-ContentSlide $presentation 5 "Proposed System" "AI-assisted infrastructure reliability workflow" {
    param($slide)
    $labels = @("Upload / Paste IaC", "AI + Rule Analysis", "Drift Score", "Timeline + Issues", "AutoFix")
    $x = 55
    for ($i = 0; $i -lt $labels.Length; $i++) {
        Add-Box $slide $x 110 155 70 $ColorCard2 $ColorAccent $true | Out-Null
        Add-Text $slide ($x + 10) 128 135 35 $labels[$i] 14 $ColorText $true "center" | Out-Null
        if ($i -lt $labels.Length - 1) { Add-Box $slide ($x + 164) 142 32 4 $ColorAccent -1 | Out-Null }
        $x += 190
    }
    Add-InfoCard $slide 85 260 350 170 "Frontend + Backend" @("Chat-style workflow", "Provider selection", "Normalized results", "Rule fallback") $ColorAccent
    Add-InfoCard $slide 525 260 350 170 "Results + Fixes" @("Score and timeline", "Issue cards", "Optional email", "Reviewable patches") $ColorGreen
}

Add-ContentSlide $presentation 6 "System Architecture" "Frontend, backend, AI providers, and AutoFix" {
    param($slide)
    Add-InfoCard $slide 65 105 240 115 "React + Vite Frontend" @("Home page", "Login/Register", "Protected dashboard") $ColorAccent
    Add-InfoCard $slide 360 105 240 115 "FastAPI Backend" @("/analyze", "/auth", "/autofix") $ColorAccent
    Add-InfoCard $slide 655 105 240 115 "AI Providers" @("Ollama", "Gemini", "Oumi RL") $ColorAccent
    Add-InfoCard $slide 65 290 240 150 "Auth Layer" @("JWT token", "SQLite users", "bcrypt password hashing") $ColorGreen
    Add-InfoCard $slide 360 290 240 150 "Analyzer Service" @("Provider/model selection", "AI analysis", "Terraform/K8s rules") $ColorAccent
    Add-InfoCard $slide 655 290 240 150 "AutoFix Path" @("ClineAgent wrapper", "Unified diff generation", "Patch application endpoint") $ColorOrange
}

Add-ContentSlide $presentation 7 "Modules and Tech Stack" "Major building blocks" {
    param($slide)
    Add-InfoCard $slide 58 115 260 320 "Frontend" @("React 19", "TypeScript + Vite", "React Router", "Tailwind CSS", "Framer Motion") $ColorAccent
    Add-InfoCard $slide 350 115 260 320 "Backend" @("FastAPI", "Pydantic", "SQLAlchemy + SQLite", "JWT auth", "SMTP email summaries") $ColorGreen
    Add-InfoCard $slide 642 115 260 320 "AI + Automation" @("Ollama local models", "Gemini cloud model", "Oumi RL scoring", "Cline AutoFix workflow") $ColorOrange
}

Add-ContentSlide $presentation 8 "Key Features" "User-facing capabilities" {
    param($slide)
    Add-Box $slide 70 110 390 330 $ColorCard (Rgb 35 48 68) $true | Out-Null
    Add-Bullets $slide 100 145 330 250 @("Authenticated dashboard", "Terraform and Kubernetes file support", "Local and cloud AI selection", "Drift score and issue cards", "Timeline prediction", "Optional result email delivery") 18 $ColorText | Out-Null
    Add-Box $slide 545 118 310 72 $ColorAccent -1 $true | Out-Null
    Add-Text $slide 580 140 240 28 "Outcome" 22 $ColorWhite $true "center" | Out-Null
    Add-Box $slide 545 220 310 170 $ColorCard2 (Rgb 35 48 68) $true | Out-Null
    Add-Text $slide 575 250 250 110 "InfraPilot turns infrastructure files into clear risk insight, practical fix suggestions, and reviewable patches." 22 $ColorText $true "center" | Out-Null
}

Add-ContentSlide $presentation 9 "Implementation Workflow" "How a single analysis request is processed" {
    param($slide)
    Add-Box $slide 72 112 820 330 $ColorCard (Rgb 35 48 68) $true | Out-Null
    Add-Text $slide 105 140 760 250 "1. User logs in and opens the protected dashboard.`r2. User pastes or attaches Terraform/Kubernetes content.`r3. Frontend sends content, file type, model, and optional email to POST /analyze.`r4. Backend selects Ollama, Gemini, Oumi, or fallback rule engine.`r5. Analyzer normalizes issues, adds Oumi scores, and calculates drift score.`r6. Frontend displays score, timeline, issues, and provider metadata.`r7. Optional AutoFix endpoint generates a unified diff patch." 16 $ColorText | Out-Null
}

Add-ContentSlide $presentation 10 "Testing and Verification" "How the project was checked" {
    param($slide)
    Add-InfoCard $slide 58 115 260 320 "Backend Checks" @("FastAPI routes inspected", "Auth flow designed around endpoints", "Email is non-blocking/background") $ColorGreen
    Add-InfoCard $slide 350 115 260 320 "Frontend Checks" @("npm run build passes", "Routing and protected pages wired", "Responsive homepage and auth pages themed") $ColorAccent
    Add-InfoCard $slide 642 115 260 320 "Resilience" @("Rule-engine fallback", "Ollama timeout configuration", "Graceful email failure handling") $ColorOrange
}

Add-ContentSlide $presentation 11 "Future Scope" "Possible improvements" {
    param($slide)
    Add-Box $slide 72 112 820 330 $ColorCard (Rgb 35 48 68) $true | Out-Null
    Add-Bullets $slide 105 145 760 240 @("Add persistent analysis history per user.", "Support Docker Compose, Helm charts, and CloudFormation.", "Integrate CI/CD scanning for pull requests.", "Add downloadable PDF summaries.", "Improve AutoFix safety with policy checks.", "Add role-based access for teams.") 18 $ColorText | Out-Null
}

Add-ContentSlide $presentation 12 "Conclusion" "InfraPilot as an infrastructure reliability assistant" {
    param($slide)
    Add-Box $slide 80 120 800 230 $ColorCard (Rgb 35 48 68) $true | Out-Null
    Add-Text $slide 115 150 730 150 "InfraPilot helps developers and platform engineers detect infrastructure risk earlier.`r`rIt combines AI analysis, rule fallback, Oumi scoring, authentication, optional email delivery, and AutoFix workflows.`r`rThe result is a practical tool for improving cloud reliability and reducing manual review effort." 20 $ColorText | Out-Null
    Add-Text $slide 325 405 310 55 "Thank You" 36 $ColorGreen $true "center" | Out-Null
}

if (Test-Path $ProjectPath) { Remove-Item $ProjectPath -Force }
if (Test-Path $DesktopPath) { Remove-Item $DesktopPath -Force }

$presentation.SaveAs($ProjectPath, $ppSaveAsOpenXMLPresentation)
$presentation.SaveAs($DesktopPath, $ppSaveAsOpenXMLPresentation)
$presentation.Close()
$powerPoint.Quit()

[System.Runtime.Interopservices.Marshal]::ReleaseComObject($presentation) | Out-Null
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($powerPoint) | Out-Null

Write-Host "Created:"
Write-Host $ProjectPath
Write-Host $DesktopPath
