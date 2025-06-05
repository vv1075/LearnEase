package main

import (
	"encoding/json"
	"io/ioutil"
)

var quizzes []Quiz
var submissions []Submission

func loadQuizzesFromFile() {
	data, err := ioutil.ReadFile("data/quizzes.json")
	if err == nil {
		json.Unmarshal(data, &quizzes)
	}
}

func saveQuizzesToFile() {
	data, _ := json.MarshalIndent(quizzes, "", "  ")
	_ = ioutil.WriteFile("data/quizzes.json", data, 0644)
}
