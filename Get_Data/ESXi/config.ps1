# Import-Module Vmware.PowerCLI -Verbose:$false | Out-Null #Import PowerCLI Module
Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false 1>$null 2>$null #Set trust certificate for remote VSphere servers

$output = ''

foreach($server in $args) {

    #Connect to VSphere server
    Connect-VIServer -Server $server -Protocol https -User root -Password customer1! 1>$null 2>$null

    #Start executing remote commands

    #Get ESXi hostname
    $esxcli = Get-EsxCli -V2
    $output = $output + $esxcli.system.hostname.get.Invoke().hostname + ','

    #Get version
    $output = $output + ((Get-vmHost | Select-Object -Property Version).Version | Out-String).trim() + ','

    #Get License
    $license = ((Get-VMHost | Select-Object -Property Name,LicenseKey).LicenseKey | Out-String).trim()
    if ($null -ne $license){
        $output = $output + "true" + ','
    }
    else {
        $output = $output + "false" + ','
    }

    #Get datastores number
    $output = $output + (Get-Datastore | Measure-Object | Format-Wide -Property Count | Out-String).trim() + ','

    #Get VMs number
    $output = $output + (get-VM | Measure-Object | Format-Wide -Property Count | Out-String).trim() + ','

    #Get VSwitches number
    $output = $output + (Get-VirtualSwitch | Measure-Object | Format-Wide -Property Count | Out-String).trim() + ','

    $output = $output + (Get-VMHost | Sort-Object Name | Select-Object Name, @{N="NTPServer";E={$_ |Get-VMHostNtpServer}}, @{N="ServiceRunning";E={(Get-VmHostService -VMHost $_ | Where-Object {$_.key-eq "ntpd"}).Running}}).NTPserver

    $output = $output + ' next '

    Disconnect-VIServer -Server $server -confirm:$false
}

# $output.Substring(0,$output.Length-6)

#Get port group nums
#$pgNum = (Get-VirtualPortGroup | Measure-Object | Format-Wide -Property Count | Out-String).trim()
# Write-Output($dsNum + ',' + $vmsNum + ',' + $vsNum +',' + $license) # + ',' + $pgNum
Write-Output $output