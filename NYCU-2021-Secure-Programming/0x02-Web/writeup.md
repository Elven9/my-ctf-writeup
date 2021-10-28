# 0x02 Web Writeup

## Homework - Imgura [100]

- 題目網址：[https://imgura.chal.h4ck3r.quest/](https://imgura.chal.h4ck3r.quest/)
- 助教給的提示：`Information Leak`、`Upload`、`LFI` (老實說提示的滿兇的XD)
- Imgura 資料夾中的項目：
  - `leak_src.zip`：透過 `.git` 還原出的原始檔
  - `prev_commit_src`：還原上一個 Commit 的 Source Code
  - `Retro9IsMe.png.php`：攻擊 Payload
  - `Retro9IsMe.png`：偽裝圖片

看到提示其實就可以猜到幾個 Information Leak 的方向，有幾種可能如 Error 的 Debug 資訊沒關、robots.txt 裡或 source code 裡有些 Route 沒拿掉或沒辦法拿掉等等。但這題的 Information Leak 肇因於部署時是直接透過 git pull 後在專案根目錄直接起一個 Http Server，讓攻擊者可以存取 `.git` 資料夾還原出完整的 Source Code

![Imgura git config](./resources/Screen%20Shot%202021-10-28%20at%204.09.23%20PM.png)

透過 [Scrabble](https://github.com/denny0223/scrabble) 去還原後就可以得到整個網頁的原始碼。從 `git log` 中可以看到這個 Repo 最近的 commit 把 Dev Page 刪除了：

![Git src log](./resources/Screen%20Shot%202021-10-28%20at%204.14.37%20PM.png)

我們只要透過指令 `git reset HEAD^ --hard` 回到 First commit，就可以得到所有 Dev 的程式碼了。

從這些程式碼中可以看到，這個頁面「曾經」有一個 dev_test_page 的存在，裏面有 Upload 功能以及 Share Image 的功能。為什麼是說「曾經」呢？理論上這些檔案本不應該存在在根目錄了，但實際上切到 `https://imgura.chal.h4ck3r.quest/dev_test_page/?page=pages/share` 路徑上仍可以看到舊的頁面，這邊真的滿起怪的，也許是題目故意設計的吧。

![Imgura dev src page](./resources/Screen%20Shot%202021-10-28%20at%204.22.26%20PM.png)

總之分析過程式碼後可以得到兩個漏洞，分別是**上傳 Filter 實作上的缺陷**以及**HomePage 時做切換頁面的方法導致的 LFI 漏洞**。

Filter 功能的漏洞如下：

```php
# 這裏居然預設是取第二個 Split 元素，直接預設整個檔名中只會有一個 dot
# bypass 的方法只要在檔名中多加一個 .png 或其他可接受的 extension 就可了
$extension = strtolower(explode(".", $filename)[1]);

if (!in_array($extension, ['png', 'jpeg', 'jpg']) !== false) {
    die("Invalid file extension: $extension.");
}

# 這個 check 方法會 Check 檔案的第一個 File，假設今天這個檔案是由兩種不同的檔案接在一起的話，就可以 Bypass 掉這條限制
$finfo = finfo_open(FILEINFO_MIME_TYPE);
$type = finfo_file($finfo, $_FILES['image_file']['tmp_name']);
finfo_close($finfo);
if (!in_array($type, ['image/png', 'image/jpeg'])) {
    die('Not an valid image.');
}

# 濾掉 <?php ....
# 這個就有一堆 Bypass 方法了，黑名單永遠是最不好的方法
$content = file_get_contents($_FILES['image_file']['tmp_name']);
if (stripos($content, "<?php") !== false) {
    die("Hacker?");
}
```

其他限制就滿簡單的如檔案大小、width、height 等等就滿簡單可以 Bypass 掉。

第二個漏洞來自於 index page 實作 router 的方法導致的 LFI:

```html
<div class="hero-body">
  <?php
  include ($_GET['page'] ?? 'pages/main') . ".php";
  ?>
</div>
```

所以最終的攻擊手法：

1. 在一個 legit 的 png (`Retro9IsMe.png`) 檔後新增一小段 php script (`<?=system($_GET["cmd"]);?>`)
2. 改檔名成 `Retro9IsMe.png.php`
3. 把檔案透過上傳功能上傳到伺服器
4. 把首頁 `page` query 改成檔案位置，並加上 cmd query 執行 Commmad
5. Navigator 後找到 Flag 檔案

## Homework - Screensaver [200]
