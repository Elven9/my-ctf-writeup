package main

import (
	"fmt"
	"log"

	"github.com/gorilla/sessions"

	"net/http"
)

func main() {
	store := sessions.NewCookieStore([]byte("d2908c1de1cd896d90f09df7df67e1d4"))

	http.HandleFunc("/get", func(w http.ResponseWriter, r *http.Request) {
		payload := r.URL.Query()["username"][0]
		fmt.Println(payload)

		session, _ := store.Get(r, "session")
		session.Values["username"] = payload
		err := session.Save(r, w)
		if err != nil {
			log.Println(err)
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	})

	http.HandleFunc("/test", func(w http.ResponseWriter, r *http.Request) {
		session, _ := store.Get(r, "session")

		username := session.Values["username"]
		if session.Values["username"] == nil {
			http.Redirect(w, r, "/login", http.StatusFound)
			return
		}

		fmt.Println(username)
	})

	fmt.Println("Start to Serve at 8888")
	http.ListenAndServe(":8888", nil)
}
