Add-Type -AssemblyName System.Windows.Forms

# Création de la fenêtre principale
$Form = New-Object System.Windows.Forms.Form
$Form.Text = "EGC Navigateur Web"
$Form.Size = New-Object System.Drawing.Size(1200, 800)

# Création de la barre d'adresse
$UrlBox = New-Object System.Windows.Forms.TextBox
$UrlBox.Size = New-Object System.Drawing.Size(1000, 20)
$UrlBox.Location = New-Object System.Drawing.Point(10, 10)

# Création du bouton "Go"
$GoButton = New-Object System.Windows.Forms.Button
$GoButton.Text = "Go"
$GoButton.Size = New-Object System.Drawing.Size(50, 20)
$GoButton.Location = New-Object System.Drawing.Point(1020, 10)

# Création du contrôle WebBrowser
$Browser = New-Object System.Windows.Forms.WebBrowser
$Browser.Size = New-Object System.Drawing.Size(1180, 700)
$Browser.Location = New-Object System.Drawing.Point(10, 40)

# Fonction pour charger une page Web
function Load-WebPage {
    param([string]$Url)

    if ($Url -notmatch "^https?://") {
        $Url = "https://$Url"
    }
    $Browser.Navigate($Url)
}

# Gestion des événements
$GoButton.Add_Click({
    Load-WebPage -Url $UrlBox.Text
})

$UrlBox.Add_KeyDown({
    param([System.Windows.Forms.KeyEventArgs]$e)
    if ($e.KeyCode -eq [System.Windows.Forms.Keys]::Enter) {
        Load-WebPage -Url $UrlBox.Text
    }
})

# Ajout des contrôles au formulaire
$Form.Controls.Add($UrlBox)
$Form.Controls.Add($GoButton)
$Form.Controls.Add($Browser)

# Chargement de la page d'accueil
$Browser.Navigate("http://www.google.com")

# Définir la priorité du processus sur "High" pour de meilleures performances
$process = Get-Process -Id $PID
$process.PriorityClass = [System.Diagnostics.ProcessPriorityClass]::High

# Affichage de la fenêtre
$Form.ShowDialog()
