package main

import (
	"log"
	"net/http"
)

func main() {
	loadQuizzesFromFile()

	router := setupRouter()
	log.Println("Server running on port 8080")
	log.Fatal(http.ListenAndServe(":8080", router))
}
