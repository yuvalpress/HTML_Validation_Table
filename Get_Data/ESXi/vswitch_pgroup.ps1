Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false 1>$null 2>$null #Set trust certificate for remote VSphere servers

Connect-VIServer -Server $args[0] -User root -Password customer1!


$oneVs = (Get-VirtualPortGroup | Select-Object -Property Name,VirtualSwitch).VirtualSwitch #get one vswitch name for every vswitch
$outputoneVs = ''

foreach($vs in $oneVs) {
    if($outputoneVs -match $vs) {
        $null
    }
    else {
        $outputoneVs += [string]$vs + ','
    }
}

$outputoneVs = $outputoneVs -replace ".$" #Delete last coma

$vss = (Get-VirtualPortGroup | Select-Object -Property Name,VirtualSwitch).VirtualSwitch #get all vswitches
$outputVS = ''

foreach($vs in $vss) {
    $outputVS += [string]$vs + ','
}

$outputVS = $outputVS -replace ".$" #Delete last coma

$pgs = (Get-VirtualPortGroup | Select-Object -Property Name,VirtualSwitch).Name #Get all port groups
$outputGP = ''

foreach($gp in $pgs) {
    $outputGP += $gp + ','
}

$outputGP = $outputGP -replace ".$" #Delete last coma

Disconnect-VIServer -Server $args[0] -confirm:$false

Write-Output $outputoneVs
Write-Output $outputVS
Write-Output $outputGP