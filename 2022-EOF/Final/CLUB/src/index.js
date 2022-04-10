const express = require("express");
const session = require("express-session");
const SqliteStore = require("express-sqlite3")(session);
const bodyParser = require("body-parser");
const path = require("path");
const fs = require("fs");
const YAML = require("yaml");
const { sha256, isNumberStr, isColorStr } = require("./utils");
const Users = require("./users");

const app = express();
const PORT = 3000;

// My Own Observation
const GlobalCounter = 0;

app.set("view engine", "ejs");
app.use(bodyParser.urlencoded({ extended: false }));
app.use(
    session({
        store: new SqliteStore({ db: "storage/db.sqlite3" }),
        secret: process.env.SESSION_SECRET,
        resave: false,
        saveUninitialized: true,
        cookie: { secure: false },
    })
);

const requireLogin = function (req, res, next) {
    if (req.session.username) {
        next();
    } else {
        res.status(403).send("login required");
    }
};

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
const loadConfig = function (configPath) {
    const normalizedPath = path.resolve("/", configPath);
    const configStr = fs.readFileSync(`./storage${normalizedPath}`, "utf8");
    const config = YAML.parse(configStr);
    if (!isNumberStr(config.group)) {
        config.group = "0";
    }
    config.group = Math.max(0, Math.min(2, Number(config.group)));
    if (!isColorStr(config.bgColor)) {
        config.bgColor = "#fff";
    }
    if (!isColorStr(config.color)) {
        config.color = "#000";
    }
    return config;
};

app.use("/static", express.static("static"));

app.get("/", ensureConfig(false), async (req, res) => {
    if (req.session.username) {
        const configPath = await Users.getConfig(req.session.username);
        const config = loadConfig(configPath);
        res.render("posts", { username: req.session.username, config });
    } else {
        res.render("index");
    }
});

app.get("/profile", requireLogin, ensureConfig(), async (req, res) => {
    const configPath = await Users.getConfig(req.session.username);
    const config = loadConfig(configPath);
    if (config.group <= 2) {
        res.render("profile", { username: req.session.username, config });
    } else {
        const messagesList = await Users.getAllMessages();
        const parsed = [];
        for (const { username, messages } of messagesList) {
            if (messages === "") {
                continue;
            }
            const messageHashes = messages.split(",");
            for (const messageHash of messageHashes) {
                const rawMessage = fs.readFileSync(
                    `./storage/${messageHash}.json`,
                    "utf8"
                );
                const message = JSON.parse(rawMessage);

                let title = "(empty)",
                    content = "(empty)";
                if (message.title) title = message.title;
                if (message.content) content = message.content;

                parsed.push({ title, content, username });
            }
        }
        res.render("admin", {
            messages: parsed,
            username: "admin",
            config: { bgColor: "#00f", color: "#0f0" },
        });
    }
});

app.get("/logout", requireLogin, (req, res) => {
    delete req.session.username;
    res.redirect("/");
});

app.post("/login", async (req, res) => {
    await Users.tryCreate(req.body.username);
    req.session.username = req.body.username;
    res.redirect("/");
});

app.post("/update", requireLogin, async (req, res) => {
    await Users.setConfig(req.session.username, req.body.config);
    res.redirect("/profile");
});

app.post("/sendMessage", requireLogin, async (req, res) => {
    const message = JSON.stringify(req.body);
    const messageHash = sha256(message);

    console.log(`FILE: ${messageHash}.json`)

    fs.writeFileSync(`./storage/${messageHash}.json`, message);

    let messages = await Users.getMessages(req.session.username);
    if (messages === "") {
        messages = messageHash;
    } else {
        messages += `,${messageHash}`;
    }
    await Users.setMessages(req.session.username, messages);

    res.redirect("/");
});

app.listen(PORT, () => {
    console.log(`Listening on port ${PORT}`);
});
