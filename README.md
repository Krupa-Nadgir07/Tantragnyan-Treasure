# Tantragnyan Treasure  
*A Competitive Programming Preparation Management System*

## 📌 Overview

**Tantragnyan Treasure** is a web-based platform designed to assist learners in competitive programming (CP) preparation. It offers centralized progress tracking, collaborative learning features, and content sharing through an integrated blogging system.

---

## 🎯 Features

### 👨‍🎓 Learner Module
- **Progress Tracking:** Visualizes attempted/solved problems across multiple CP platforms.
- **Goal Setting:** Set and track daily, weekly, and monthly learning objectives.
- **Bookmarking:** Save important problems for later review.
- **Topic-wise Learning:** Study categorized topics and subtopics systematically.
- **Study Groups:** Automatically generated using clustering algorithms for peer collaboration.

### ✍️ Blogger Module
- **Blog Creation:** Rich-text blog editor with media and topic tagging.
- **Pre-Blog Setup:** Add title, description, and topic before publishing.
- **Content Display:** Organized under topics for structured browsing by learners.

---

## 🛠️ Technology Stack

### Backend
- Django (Python)
- Machine Learning: Scikit-learn, Pandas, UMAP, Agglomerative Clustering

### Frontend
- Bootstrap (with Bootswatch Minty theme)
- TinyMCE (Rich Text Editor)

### Database
- **PostgreSQL:** Structured data (users, goals, problems)
- **MongoDB:** Unstructured data (study groups, activity logs, company-topic mappings)

---

## 🧠 Machine Learning

- Learner interests encoded as binary vectors.
- Clustering via Agglomerative Clustering.
- Visualized with UMAP and dendrograms.
- **Metrics:**
  - Silhouette Score: `0.6039`
  - Davies-Bouldin Index: `0.5127`
  - Calinski-Harabasz Index: `62.7846`
