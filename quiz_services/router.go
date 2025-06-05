package main

import (
	"net/http"

	"github.com/gorilla/mux"
)

func setupRouter() *mux.Router {
	router := mux.NewRouter()

	// ✅ Routes for Quiz Management
	router.HandleFunc("/quizzes", createQuiz).Methods("POST")
	router.HandleFunc("/quizzes", getQuizzes).Methods("GET")
	router.HandleFunc("/quizzes/{quiz_id}", getQuizByID).Methods("GET")
	router.HandleFunc("/quizzes/{quiz_id}", updateQuiz).Methods("PUT")
	router.HandleFunc("/quizzes/{quiz_id}/questions", addQuestion).Methods("POST")
	router.HandleFunc("/quizzes/{quiz_id}/submit", submitQuiz).Methods("POST")
	router.HandleFunc("/quizzes/{quiz_id}/results", getQuizResults).Methods("GET")
	router.HandleFunc("/quizzes/{quiz_id}", deleteQuiz).Methods("DELETE")
	router.HandleFunc("/generate-ai-quiz", generateAIQuizHandler).Methods("POST")

	// ✅ Allow preflight CORS (OPTIONS request handler)
	router.Methods("OPTIONS").HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		enableCORS(w)
		w.WriteHeader(http.StatusOK)
	})

	return router
}
