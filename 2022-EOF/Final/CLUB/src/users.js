const sqlite3 = require("sqlite3");

const db = new sqlite3.Database("./storage/db.sqlite3");
db.run(
    "CREATE TABLE IF NOT EXISTS Users (username TEXT UNIQUE, config TEXT, messages TEXT DEFAULT '')"
);

class Users {
    static tryCreate(username) {
        return new Promise((resolve, reject) => {
            db.run(
                "INSERT OR IGNORE INTO Users (username) VALUES (?)",
                [username],
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

    static getConfig(username) {
        return new Promise((resolve, reject) => {
            db.get(
                "SELECT config FROM Users WHERE username = ?",
                [username],
                (err, row) => {
                    if (err) {
                        reject(err);
                    } else {
                        resolve(row.config);
                    }
                }
            );
        });
    }
    static setConfig(username, config) {
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

    static getMessages(username) {
        return new Promise((resolve, reject) => {
            db.get(
                "SELECT messages FROM Users WHERE username = ?",
                [username],
                (err, row) => {
                    if (err) {
                        reject(err);
                    } else {
                        resolve(row.messages);
                    }
                }
            );
        });
    }
    static setMessages(username, messages) {
        return new Promise((resolve, reject) => {
            db.run(
                "UPDATE Users SET messages = ? WHERE username = ?",
                [messages, username],
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

    static getAllMessages() {
        return new Promise((resolve, reject) => {
            db.all("SELECT username, messages FROM Users", (err, rows) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(rows);
                }
            });
        });
    }
}

module.exports = Users;
