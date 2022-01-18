<?php
// using php:7.4-apache Dokcer image
// Show Src Code
isset($_GET['8']) && ($_GET['8'] === '===D') && die(show_source(__FILE__, 1));

// Create Sandbox Env
!file_exists($dir = "sandbox/" . md5(session_start().session_id())) && mkdir($dir);

chdir($dir);
!isset($_GET['code']) && die('/?8====D');

// 可以寫到任意地方
$time = date('Y-m-d-H:i:s'); 
strlen($out = ($_GET['output'] ?? "$time.html" )) > 255 && die('toooooooo loooooong');

(trim($ext=pathinfo($out)['extension']) !== '' && 
strtolower(substr($ext, 0, 2)) !== "ph") ? 
    file_put_contents($out, sprintf(file_get_contents('/var/www/html/template.html'), $time, highlight_string($_GET['code'],true))) :
    die("BAD"); 

echo "<p>Highlight:<a href=\"/$dir/$out\">$out</a></p>"

// You might also need: /phpinfo.php
