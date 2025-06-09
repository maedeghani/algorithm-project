import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import numpy as np
import json
from hazm import sent_tokenize
import re
from collections import Counter
from difflib import SequenceMatcher

# مدل از پیش‌آموزش‌دیده فارسی
MODEL_NAME = "HooshvareLab/bert-base-parsbert-uncased"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

# ۱. بهبود استخراج ویژگی‌ها با میانگین‌گیری از تمام توکن‌ها
def get_embeddings(text, pooling_method="cls"):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # روش‌های مختلف استخراج ویژگی
    if pooling_method == "cls":
        # استفاده از توکن CLS
        return outputs.last_hidden_state[:, 0, :].numpy().squeeze()
    elif pooling_method == "mean":
        # میانگین‌گیری از تمام توکن‌ها
        attention_mask = inputs["attention_mask"]
        mean_embedding = torch.sum(outputs.last_hidden_state * attention_mask.unsqueeze(-1), 1) / torch.sum(attention_mask, 1, keepdim=True)
        return mean_embedding.numpy().squeeze()
    elif pooling_method == "max":
        # حداکثر مقدار هر بعد
        attention_mask = inputs["attention_mask"]
        # ماسک کردن پدینگ‌ها با مقدار منفی بزرگ
        masked = outputs.last_hidden_state * attention_mask.unsqueeze(-1) - (1 - attention_mask.unsqueeze(-1)) * 1e9
        max_embedding = torch.max(masked, dim=1)[0]
        return max_embedding.numpy().squeeze()
    else:
        raise ValueError(f"روش استخراج ویژگی {pooling_method} پشتیبانی نمی‌شود.")

# ۲. تجزیه متن به جملات و مقایسه جمله به جمله
def find_matching_segments(text1, text2, min_sim=0.7):
    # تقسیم متن به جملات با hazm
    sentences1 = sent_tokenize(text1)
    sentences2 = sent_tokenize(text2)
    
    # حذف جملات خالی
    sentences1 = [s.strip() for s in sentences1 if s.strip()]
    sentences2 = [s.strip() for s in sentences2 if s.strip()]
    
    matching_segments = []
    
    # مقایسه جمله به جمله
    for i, s1 in enumerate(sentences1):
        for j, s2 in enumerate(sentences2):
            # برای جملات کوتاه از SequenceMatcher استفاده می‌کنیم
            if len(s1) < 50 or len(s2) < 50:
                ratio = SequenceMatcher(None, s1, s2).ratio()
                if ratio >= min_sim:
                    matching_segments.append({
                        "segment1": {"text": s1, "index": i},
                        "segment2": {"text": s2, "index": j},
                        "similarity": ratio
                    })
            else:
                # برای جملات بلندتر از مدل زبانی استفاده می‌کنیم
                emb1 = get_embeddings(s1, "mean")
                emb2 = get_embeddings(s2, "mean")
                sim = float(cosine_similarity([emb1], [emb2])[0][0])
                
                if sim >= min_sim:
                    matching_segments.append({
                        "segment1": {"text": s1, "index": i},
                        "segment2": {"text": s2, "index": j},
                        "similarity": sim
                    })
    
    return matching_segments

# ۳. تحلیل آماری متن
def get_text_statistics(text):
    # تعداد کلمات
    words = re.findall(r'\b\w+\b', text)
    word_count = len(words)
    
    # تعداد جملات
    sentences = sent_tokenize(text)
    sentence_count = len([s for s in sentences if s.strip()])
    
    # میانگین طول جملات
    avg_sentence_length = word_count / max(1, sentence_count)
    
    # فراوانی کلمات
    word_freq = Counter(words)
    most_common = word_freq.most_common(5)
    
    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_sentence_length": avg_sentence_length,
        "most_common_words": most_common
    }

# ۴. بهبود مقایسه دانشجویان
def compare_students(student_answers, question_id, min_sim=0.7, suspicious_threshold=0.85):
    results = []
    student_ids = list(student_answers.keys())
    
    # محاسبه آمار متنی برای هر پاسخ
    text_stats = {}
    for student_id, answer in student_answers.items():
        text_stats[student_id] = get_text_statistics(answer)
    
    for i in range(len(student_ids)):
        for j in range(i + 1, len(student_ids)):
            s1, s2 = student_ids[i], student_ids[j]
            a1, a2 = student_answers[s1], student_answers[s2]
            
            # ۵. استفاده از روش‌های مختلف استخراج ویژگی
            # مقایسه با CLS token
            emb1_cls = get_embeddings(a1, "cls")
            emb2_cls = get_embeddings(a2, "cls")
            sim_cls = float(cosine_similarity([emb1_cls], [emb2_cls])[0][0])
            
            # مقایسه با میانگین توکن‌ها
            emb1_mean = get_embeddings(a1, "mean")
            emb2_mean = get_embeddings(a2, "mean")
            sim_mean = float(cosine_similarity([emb1_mean], [emb2_mean])[0][0])
            
            # میانگین نمرات شباهت
            sim_score = (sim_cls + sim_mean) / 2
            
            # ۶. یافتن قطعات مشابه
            matching_segments = find_matching_segments(a1, a2, min_sim)
            
            # ۷. محاسبه شباهت آماری
            stats1 = text_stats[s1]
            stats2 = text_stats[s2]
            
            # شباهت در تعداد کلمات (نسبت کوچکتر به بزرگتر)
            word_count_ratio = min(stats1["word_count"], stats2["word_count"]) / max(1, max(stats1["word_count"], stats2["word_count"]))
            
            # شباهت در میانگین طول جملات
            sentence_length_ratio = min(stats1["avg_sentence_length"], stats2["avg_sentence_length"]) / max(1, max(stats1["avg_sentence_length"], stats2["avg_sentence_length"]))
            
            # ۸. ترکیب معیارهای مختلف برای تعیین سطح ریسک
            # وزن‌دهی به معیارهای مختلف
            semantic_weight = 0.6  # وزن شباهت معنایی
            segment_weight = 0.3   # وزن قطعات مشابه
            stats_weight = 0.1     # وزن شباهت آماری
            
            # محاسبه نمره نهایی
            segment_sim = sum([s["similarity"] for s in matching_segments]) / max(1, len(matching_segments)) if matching_segments else 0
            stats_sim = (word_count_ratio + sentence_length_ratio) / 2
            
            final_score = (sim_score * semantic_weight + 
                          segment_sim * segment_weight + 
                          stats_sim * stats_weight)
            
            # تعیین سطح ریسک
            if final_score >= suspicious_threshold:
                risk = "HIGH"
            elif final_score >= min_sim:
                risk = "MEDIUM"
            else:
                risk = "LOW"
            
            # ۹. گزارش دقیق‌تر
            formatted_segments = []
            for segment in matching_segments:
                s1_text = segment["segment1"]["text"]
                s2_text = segment["segment2"]["text"]
                s1_start = a1.find(s1_text)
                s2_start = a2.find(s2_text)
                
                formatted_segments.append({
                    "question_id": question_id,
                    "segment1": {
                        "text": s1_text,
                        "start_index": s1_start,
                        "end_index": s1_start + len(s1_text) if s1_start >= 0 else -1
                    },
                    "segment2": {
                        "text": s2_text,
                        "start_index": s2_start,
                        "end_index": s2_start + len(s2_text) if s2_start >= 0 else -1
                    },
                    "similarity_percentage": round(segment["similarity"] * 100, 2)
                })
            
            results.append({
                "student_pair": {
                    "student1_id": s1,
                    "student2_id": s2
                },
                "similarity_scores": {
                    "cls_similarity": round(sim_cls, 4),
                    "mean_similarity": round(sim_mean, 4),
                    "final_score": round(final_score, 4)
                },
                "text_statistics_similarity": {
                    "word_count_ratio": round(word_count_ratio, 4),
                    "sentence_length_ratio": round(sentence_length_ratio, 4)
                },
                "matching_segments": formatted_segments,
                "matching_segment_count": len(formatted_segments),
                "overall_risk_level": risk,
                "confidence": round(max(0.5, min(1.0, abs(final_score - min_sim) / max(0.01, suspicious_threshold - min_sim))), 2)
            })
    
    return results

# ۱۰. بهبود خروجی JSON
def generate_results_json(quiz_id, student_answers, question_id):
    analysis_results = compare_students(student_answers, question_id)
    
    # مرتب‌سازی نتایج بر اساس نمره نهایی (نزولی)
    analysis_results.sort(key=lambda x: x["similarity_scores"]["final_score"], reverse=True)
    
    # آمار کلی
    high_risk_count = sum(1 for r in analysis_results if r["overall_risk_level"] == "HIGH")
    medium_risk_count = sum(1 for r in analysis_results if r["overall_risk_level"] == "MEDIUM")
    low_risk_count = sum(1 for r in analysis_results if r["overall_risk_level"] == "LOW")
    
    output = {
        "quiz_id": quiz_id,
        "timestamp": datetime.utcnow().isoformat(),
        "summary": {
            "total_comparisons": len(analysis_results),
            "high_risk_count": high_risk_count,
            "medium_risk_count": medium_risk_count,
            "low_risk_count": low_risk_count,
            "highest_similarity": round(analysis_results[0]["similarity_scores"]["final_score"], 4) if analysis_results else 0
        },
        "analysis_results": analysis_results,
        "analysis_metadata": {
            "algorithm_version": "Enhanced-Embedding-v2",
            "model_used": MODEL_NAME,
            "threshold_settings": {
                "minimum_similarity": 0.7,
                "suspicious_threshold": 0.85
            },
            "weighting": {
                "semantic_weight": 0.6,
                "segment_weight": 0.3,
                "stats_weight": 0.1
            }
        }
    }
    return output

# مثال استفاده:
if __name__ == "__main__":
    answers = {
        "stu_1": "نظریه داروین درباره انتخاب طبیعی به تکامل گونه‌ها اشاره دارد. این نظریه بیان می‌کند که موجوداتی که با محیط خود سازگارتر هستند، شانس بیشتری برای بقا و تولیدمثل دارند.",
        "stu_2": "نظریه انتخاب طبیعی داروین به تکامل موجودات زنده اشاره می‌کند. طبق این نظریه، جانورانی که با محیط خود سازگاری بهتری دارند، احتمال بیشتری برای زنده ماندن و تولیدمثل دارند.",
        "stu_3": "پاسخ به سوال مربوط به داروین را نمی‌دانم. اما فکر می‌کنم چیزی در مورد تکامل بود."
    }

    result_json = generate_results_json("quiz_1403_01", answers, "q_1")
    
    with open("results_improved.json", "w", encoding="utf-8") as f:
        json.dump(result_json, f, ensure_ascii=False, indent=2)
    
    print("تحلیل تقلب با موفقیت انجام شد و نتایج در فایل results_improved.json ذخیره شد.")

