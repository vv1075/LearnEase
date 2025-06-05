package main

import (
	"bytes"

	"io/ioutil"

	"encoding/json"
	"math/rand"
	"net/http"
	"time"

	"fmt"
	"strings"

	"github.com/google/uuid"
	"github.com/gorilla/mux"
)

func enableCORS(w http.ResponseWriter) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
}

func createQuiz(w http.ResponseWriter, r *http.Request) {
	var quiz Quiz
	json.NewDecoder(r.Body).Decode(&quiz)
	quiz.ID = uuid.New().String()
	quiz.LastUpdated = time.Now().Unix()

	// 💥 Make sure CourseID is not empty
	fmt.Println("📦 Received Quiz CourseID from Django:", quiz.CourseID)

	quizzes = append(quizzes, quiz)

	enableCORS(w)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(quiz)
}

func getQuizzes(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(quizzes)
}

func getQuizByID(w http.ResponseWriter, r *http.Request) {
	params := mux.Vars(r)
	quizID := params["quiz_id"]
	enableCORS(w)

	for _, quiz := range quizzes {
		if quiz.ID == quizID {
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(quiz)
			return
		}
	}
	http.Error(w, "Quiz not found", http.StatusNotFound)
}

func updateQuiz(w http.ResponseWriter, r *http.Request) {
	params := mux.Vars(r)
	quizID := params["quiz_id"]
	enableCORS(w)

	var updatedQuiz Quiz
	json.NewDecoder(r.Body).Decode(&updatedQuiz)

	for i, quiz := range quizzes {
		if quiz.ID == quizID {
			quizzes[i].Title = updatedQuiz.Title
			var cleanQuestions []Question

			for j, q := range updatedQuiz.Questions {
				// Rebuild question struct to enforce types
				cleanQuestion := Question{
					ID:      j + 1,
					Text:    q.Text,
					Options: q.Options,
					Correct: q.Correct, // ✅ should already be int
					Marks:   q.Marks,
				}
				fmt.Printf("Updated Question %d: correct=%d, marks=%d\n", j+1, q.Correct, q.Marks)
				cleanQuestions = append(cleanQuestions, cleanQuestion)
			}

			quizzes[i].Questions = cleanQuestions
			quizzes[i].LastUpdated = time.Now().Unix()

			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(quizzes[i])
			return
		}
	}
	http.Error(w, "Quiz not found", http.StatusNotFound)

}
func addQuestion(w http.ResponseWriter, r *http.Request) {
	params := mux.Vars(r)
	quizID := params["quiz_id"]
	enableCORS(w)

	var question Question
	json.NewDecoder(r.Body).Decode(&question)

	for i := range quizzes {
		if quizzes[i].ID == quizID {
			question.ID = len(quizzes[i].Questions) + 1
			quizzes[i].Questions = append(quizzes[i].Questions, question)

			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(quizzes[i])
			return
		}
	}
	http.Error(w, "Quiz not found", http.StatusNotFound)
}

func submitQuiz(w http.ResponseWriter, r *http.Request) {
	var submission Submission
	enableCORS(w)
	json.NewDecoder(r.Body).Decode(&submission)

	fmt.Println("Received submission:", submission)
	fmt.Println("Received submission:", submission.Answers) // ✅ add this
	submissions = append(submissions, submission)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"message": "Submission received"})
}

func getQuizResults(w http.ResponseWriter, r *http.Request) {
	params := mux.Vars(r)
	quizID := params["quiz_id"]
	enableCORS(w)

	var totalScore int
	var maxScore int
	var submittedAnswers []int

	// ✅ Loop backward to always take latest submission (if multiple)
	for i := len(submissions) - 1; i >= 0; i-- {
		submission := submissions[i]
		if submission.QuizID == quizID {
			submittedAnswers = submission.Answers

			// Find matching quiz
			for _, quiz := range quizzes {
				if quiz.ID == quizID {
					for i, question := range quiz.Questions {
						maxScore += question.Marks
						fmt.Printf("Comparing Answer[%d]: submitted=%d, correct=%d\n", i, submission.Answers[i], question.Correct)
						if i < len(submission.Answers) && submission.Answers[i] == question.Correct {
							totalScore += question.Marks
						}
					}
				}
			}
			break // ✅ break after first (latest) match
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"score":   totalScore,
		"max":     maxScore,
		"answers": submittedAnswers,
	})
}

func deleteQuiz(w http.ResponseWriter, r *http.Request) {
	params := mux.Vars(r)
	quizID := params["quiz_id"]
	enableCORS(w)

	for i, quiz := range quizzes {
		if quiz.ID == quizID {
			quizzes = append(quizzes[:i], quizzes[i+1:]...)
			w.WriteHeader(http.StatusOK)
			w.Write([]byte(`{"message":"Quiz deleted successfully"}`))
			return
		}
	}
	http.Error(w, "Quiz not found", http.StatusNotFound)
}

func generateAIQuizHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}

	var input struct {
		Title        string `json:"title"`
		Topic        string `json:"topic"`
		NumQuestions int    `json:"num_questions"`
		TotalMarks   int    `json:"total_marks"`
		CourseID     string `json:"course_id"`
		Status       string `json:"status"` // draft or saved
	}

	err := json.NewDecoder(r.Body).Decode(&input)
	if err != nil {
		http.Error(w, "Invalid input", http.StatusBadRequest)
		return
	}

	// 🧠 Generate AI Questions from OpenAI
	questions := callOpenAIForQuiz(input.Topic, input.NumQuestions, input.TotalMarks)

	// ✅ Validate Correct Index (0–3)
	for i := range questions {
		if questions[i].Correct < 0 || questions[i].Correct > 3 {
			fmt.Printf("⚠ Invalid correct index for Q%d: %d → Resetting to 0\n", i+1, questions[i].Correct)
			questions[i].Correct = 0
		}
	}

	// ✅ Re-balance Marks (Total = input.TotalMarks)
	sumMarks := 0
	for _, q := range questions {
		sumMarks += q.Marks
	}
	if sumMarks != input.TotalMarks {
		fmt.Println("🔁 Re-distributing marks to match total:", input.TotalMarks)
		perQ := input.TotalMarks / len(questions)
		rem := input.TotalMarks % len(questions)
		for i := range questions {
			questions[i].Marks = perQ
			if i < rem {
				questions[i].Marks++
			}
		}
	}

	// ✅ Build Quiz Struct
	quiz := Quiz{
		ID:          uuid.New().String(),
		Title:       input.Title,
		CourseID:    input.CourseID,
		Questions:   questions,
		TotalMarks:  input.TotalMarks,
		LastUpdated: time.Now().Unix(),
		Status:      input.Status,
		Source:      "ai",
	}

	// ✅ Save and Respond
	quizzes = append(quizzes, quiz)
	saveQuizzesToFile()
	enableCORS(w)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(quiz)
}
func callOpenAIForQuiz(topic string, numQuestions int, totalMarks int) []Question {
	apiKey := "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"
	rand.Seed(time.Now().UnixNano())

	baseMarks := totalMarks / numQuestions
	remainder := totalMarks % numQuestions

	// ✅ Powerful prompt to generate proper JSON
	prompt := fmt.Sprintf(`You are an expert quiz generator.
Generate %d multiple choice questions on "%s".
Each question must include:
- "text": Question text
- "options": Array of 4 strings
- "correct": Index of correct option (0–3)
- "marks": Integer (total across all questions = %d)

Respond ONLY in raw JSON format like:
[
  {
    "text": "Sample question?",
    "options": ["A", "B", "C", "D"],
    "correct": 1,
    "marks": 5
  }
]`, numQuestions, topic, totalMarks)

	reqBody := map[string]interface{}{
		"model": "gpt-3.5-turbo",
		"messages": []map[string]string{
			{"role": "user", "content": prompt},
		},
	}

	bodyBytes, _ := json.Marshal(reqBody)
	req, _ := http.NewRequest("POST", "https://api.openai.com/v1/chat/completions", bytes.NewBuffer(bodyBytes))
	req.Header.Set("Authorization", "Bearer "+apiKey)
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("❌ Error reaching OpenAI:", err)
		return fallbackDummyQuestions(topic, numQuestions, baseMarks, remainder)
	}
	defer resp.Body.Close()

	respBody, _ := ioutil.ReadAll(resp.Body)

	// Parse first stage GPT wrapper response
	var openaiResp struct {
		Choices []struct {
			Message struct {
				Content string `json:"content"`
			} `json:"message"`
		} `json:"choices"`
	}

	if err := json.Unmarshal(respBody, &openaiResp); err != nil {
		fmt.Println("❌ JSON parsing error from OpenAI response:", err)
		return fallbackDummyQuestions(topic, numQuestions, baseMarks, remainder)
	}

	content := strings.TrimSpace(openaiResp.Choices[0].Message.Content)

	// Remove ```json code block if present
	if strings.HasPrefix(content, "```json") {
		content = strings.TrimPrefix(content, "```json")
	}
	if strings.HasPrefix(content, "```") {
		content = strings.TrimPrefix(content, "```")
	}
	if strings.HasSuffix(content, "```") {
		content = strings.TrimSuffix(content, "```")
	}

	// 🧠 DEBUG Raw GPT content
	fmt.Println("📦 GPT JSON Content:\n", content)

	var questions []Question
	if err := json.Unmarshal([]byte(content), &questions); err != nil {
		fmt.Println("⚠️ Error parsing JSON content:", err)
		return fallbackDummyQuestions(topic, numQuestions, baseMarks, remainder)
	}

	// Add unique IDs
	for i := range questions {
		questions[i].ID = i
	}

	// Print questions
	for _, q := range questions {
		fmt.Printf("✅ Q: %s\n🔸 Options: %v\n✔ Correct: %s\n⭐ Marks: %d\n\n",
			q.Text, q.Options, q.Options[q.Correct], q.Marks)
	}

	return questions
}

// ✅ Fallback dummy questions if OpenAI fails
func fallbackDummyQuestions(topic string, numQuestions, baseMarks, remainder int) []Question {
	fmt.Println("⚠ Using fallback dummy questions.")
	var questions []Question
	for i := 0; i < numQuestions; i++ {
		marks := baseMarks
		if i < remainder {
			marks++
		}
		q := Question{
			ID:      i,
			Text:    fmt.Sprintf("AI Question %d on %s", i+1, topic),
			Options: []string{"Option A", "Option B", "Option C", "Option D"},
			Correct: rand.Intn(4),
			Marks:   marks,
		}
		questions = append(questions, q)
	}
	return questions
}
