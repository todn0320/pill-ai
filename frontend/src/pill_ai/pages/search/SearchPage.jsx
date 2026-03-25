import React, { useState } from "react";
import "./SearchPage.css";

const API_BASE = "http://localhost:8000";

const SearchPage = () => {
  const [searchName, setSearchName] = useState("");
  const [results, setResults] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [aiQuestion, setAiQuestion] = useState("");
  const [aiAnswer, setAiAnswer] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [filter, setFilter] = useState("전체");
  const [suggestions, setSuggestions] = useState([]); // 퍼지 검색 추천
  const [noResult, setNoResult] = useState(false);

  const filters = ["전체", "일반의약품", "전문의약품", "건강기능식품", "성분 검색"];

  // 약 검색
  const handleSearch = async (nameOverride = null) => {
    const query = nameOverride || searchName;
    if (!query.trim()) return;
    setLoading(true);
    setSelected(null);
    setAiAnswer("");
    setSuggestions([]);
    setNoResult(false);

    try {
      const res = await fetch(`${API_BASE}/drug/search?name=${encodeURIComponent(query)}&limit=20`);
      const data = await res.json();

      if (data.results?.length > 0) {
        setResults(data.results);
        setNoResult(false);
      } else {
        // 결과 없으면 퍼지 검색으로 추천
        setResults([]);
        setNoResult(true);
        const sugRes = await fetch(`${API_BASE}/drug/suggest?name=${encodeURIComponent(query)}&top=5`);
        const sugData = await sugRes.json();
        if (sugData.has_suggestions) {
          setSuggestions(sugData.suggestions);
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  // 추천 약 클릭 → 해당 이름으로 재검색
  const handleSuggestionClick = (name) => {
    setSearchName(name);
    setSuggestions([]);
    setNoResult(false);
    handleSearch(name);
  };

  // 약 상세 조회
  const handleSelect = async (item) => {
    try {
      const res = await fetch(`${API_BASE}/drug/info/${item.ITEM_SEQ}`);
      const data = await res.json();
      setSelected(data);
      setAiAnswer("");
    } catch (e) {
      setSelected(item);
    }
  };

  // AI 질문
  const handleAiAsk = async () => {
    if (!aiQuestion.trim() || !selected) return;
    setAiLoading(true);
    try {
      const res = await fetch(
        `${API_BASE}/drug/ask?question=${encodeURIComponent(aiQuestion)}&item_seq=${selected.ITEM_SEQ}&item_name=${encodeURIComponent(selected.ITEM_NAME)}`
      );
      const data = await res.json();
      setAiAnswer(data.answer || "답변을 가져오지 못했습니다.");
    } catch (e) {
      setAiAnswer("오류가 발생했습니다.");
    } finally {
      setAiLoading(false);
    }
  };

  const getOtcLabel = (code) => {
    if (!code) return "";
    if (code.includes("전문") || code === "01") return "전문의약품";
    if (code.includes("일반") || code === "02") return "일반의약품";
    return code;
  };

  return (
    <>
      {/* 검색 헤더 */}
      <div className="search-header-wrap">
        <div className="search-header-card">
          <div className="search-title">약 · 건강기능식품 검색</div>
          <div className="search-row">
            <div className="search-input-wrap">
              <span className="search-icon">
                <svg viewBox="0 0 14 14" stroke="currentColor" fill="none">
                  <circle cx="6" cy="6" r="4.5"/>
                  <line x1="9.5" y1="9.5" x2="13" y2="13" strokeLinecap="round"/>
                </svg>
              </span>
              <input
                className="search-input"
                type="text"
                value={searchName}
                onChange={(e) => setSearchName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                placeholder="제품명, 성분명으로 검색..."
              />
            </div>
            <button className="search-btn" onClick={() => handleSearch()}>검색</button>
          </div>
          <div className="filter-row">
            {filters.map((f) => (
              <button
                key={f}
                className={`filter-chip ${filter === f ? "active" : ""}`}
                onClick={() => setFilter(f)}
              >
                {f}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 결과 + 상세 */}
      <div className="body-wrap">
        {/* 결과 리스트 */}
        <div className="results-card">
          <div className="result-count">
            {loading ? "검색 중..." : results.length > 0 ? `검색 결과 ${results.length}건` : "검색어를 입력하세요"}
          </div>

          {/* 검색 결과 없을 때 퍼지 추천 UI */}
          {noResult && (
            <div className="no-result-wrap">
              <div className="no-result-text">
                "<strong>{searchName}</strong>" 검색 결과가 없어요
              </div>
              {suggestions.length > 0 && (
                <>
                  <div className="suggest-label">혹시 이 약을 찾으셨나요?</div>
                  {suggestions.map((s, i) => (
                    <div
                      key={i}
                      className="suggest-item"
                      onClick={() => handleSuggestionClick(s.item_name)}
                    >
                      <span className="suggest-icon">🔍</span>
                      <span className="suggest-name">{s.item_name}</span>
                      <span className="suggest-arr">›</span>
                    </div>
                  ))}
                </>
              )}
            </div>
          )}

          {/* 검색 결과 */}
          {results.map((item) => (
            <div
              key={item.ITEM_SEQ}
              className={`result-item ${selected?.ITEM_SEQ === item.ITEM_SEQ ? "selected" : ""}`}
              onClick={() => handleSelect(item)}
            >
              <div className="result-top">
                <div className="drug-thumb">
                  <div className="drug-pill-sm" style={{width:"18px", background:"var(--green6)"}}></div>
                </div>
                <div>
                  <div className="result-name">{item.ITEM_NAME}</div>
                  <div className="result-sub">{item.ENTP_NAME}</div>
                </div>
              </div>
              <div className="result-tags">
                <span className={`tag ${item.ETC_OTC_CODE?.includes("일반") ? "otc" : "rx"}`}>
                  {getOtcLabel(item.ETC_OTC_CODE)}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* 상세 패널 */}
        <div className="detail-card">
          {selected ? (
            <>
              <div className="detail-top">
                <div className="drug-big-icon">
                  <svg viewBox="0 0 36 18" fill="none">
                    <rect x="0" y="0" width="36" height="18" rx="9" fill="#1D9E75"/>
                    <rect x="0" y="0" width="20" height="18" rx="9" fill="#0F6E56"/>
                  </svg>
                </div>
                <div style={{flex:1}}>
                  <div className="detail-drug-name">{selected.ITEM_NAME}</div>
                  <div className="detail-drug-sub">{selected.ENTP_NAME}</div>
                  <div className="detail-tags">
                    <span className={`tag ${selected.ETC_OTC_CODE?.includes("일반") ? "otc" : "rx"}`}>
                      {getOtcLabel(selected.ETC_OTC_CODE)}
                    </span>
                  </div>
                </div>
              </div>

              {selected.EFCY_QESITM && (
                <div className="detail-section">
                  <div className="detail-section-title">효능·효과</div>
                  <p className="detail-text">{selected.EFCY_QESITM.slice(0, 300)}{selected.EFCY_QESITM.length > 300 ? "..." : ""}</p>
                </div>
              )}

              {selected.ATPN_QESITM && (
                <div className="detail-section">
                  <div className="detail-section-title">주의사항</div>
                  <div className="warn-item">
                    <div className="warn-dot"></div>
                    <span>{selected.ATPN_QESITM.slice(0, 200)}{selected.ATPN_QESITM.length > 200 ? "..." : ""}</span>
                  </div>
                </div>
              )}

              {/* AI 질문 */}
              <div className="detail-section ai-section">
                <div className="detail-section-title">AI 복약 분석</div>
                <div className="ai-input-row">
                  <input
                    className="ai-input"
                    type="text"
                    value={aiQuestion}
                    onChange={(e) => setAiQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleAiAsk()}
                    placeholder="예: 임산부가 먹어도 돼? / 부작용이 뭐야?"
                  />
                  <button className="ai-btn" onClick={handleAiAsk} disabled={aiLoading}>
                    {aiLoading ? "분석 중..." : "AI 분석"}
                  </button>
                </div>
                {aiAnswer && (
                  <div className="ai-answer">
                    <div className="ai-answer-label">AI 답변</div>
                    <p>{aiAnswer}</p>
                  </div>
                )}
              </div>

              <div className="evidence-card">
                <div className="evidence-label">근거 출처 (Evidence Card)</div>
                <div className="evidence-desc">식약처 DUR 품목 정보 · e약은요 · 확신도 High</div>
              </div>

              <div className="action-btns">
                <button className="btn-add">+ 내 약함에 추가</button>
                <button className="btn-ai">AI 복약 분석</button>
              </div>
            </>
          ) : (
            <div className="detail-empty">
              <p>검색 결과에서 약을 선택하면<br />상세 정보가 표시됩니다</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default SearchPage;
