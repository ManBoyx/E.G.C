# Ceci est un commentaire PowerShell.

function MyFunction([Parameter(Position = 0)][System.String]$path)
{
    :loopLabel foreach ($thisFile in (Get-ChildItem $path))
    {
        Write-Host ; Write-Host -Fore Yellow `
            (« Longueur : » +
            [System.Math]::Floor($thisFile.Length / 1000))
    }
}
