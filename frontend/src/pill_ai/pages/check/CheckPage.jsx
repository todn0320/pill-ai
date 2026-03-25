import React, { useState } from "react";
import "./CheckPage.css";

const API_BASE = "http://localhost:8000";

const CheckPage = () => {
  const [drugA, setDrugA] = useState("");
  const [drugB, setDrugB] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null); // null | { type, nameA, nameB, content, aiAnswer }

  const handleCheck = async () => {
    if (!drugA.trim() || !drugB.trim()) {
      alert("두 약 이름을 모두 입력해주세요.");
      return;
    }
    setLoading(true);
    setResult(null);

    try {
      // 1. 두 약 이름으로 item_seq 검색
      const [resA, resB] = await Promise.all([
        fetch(`${API_BASE}/drug/search?name=${encodeURIComponent(drugA)}&limit=1`).then(r => r.json()),
        fetch(`${API_BASE}/drug/search?name=${encodeURIComponent(drugB)}&limit=1`).then(r => r.json()),
      ]);

      const itemA = resA.results?.[0];
      const itemB = resB.results?.[0];

      if (!itemA || !itemB) {
        setResult({ type: "unknown", nameA: drugA, nameB: drugB, content: "약 정보를 찾을 수 없습니다. 정확한 약 이름을 입력해주세요.", aiAnswer: null });
        return;
      }

      // 2. DUR 병용금기 확인
      const durRes = await fetch(`${API_BASE}/drug/check?item_seq_a=${itemA.ITEM_SEQ}&item_seq_b=${itemB.ITEM_SEQ}`).then(r => r.json());

      if (durRes.is_prohibited) {
        // 3. AI 상세 분석
        const aiRes = await fetch(
          `${API_BASE}/drug/ask?question=${encodeURIComponent(itemA.ITEM_NAME + "와 " + itemB.ITEM_NAME + " 병용하면 어떤 위험이 있어?")}&item_name=${encodeURIComponent(itemA.ITEM_NAME)}`
        ).then(r => r.json());

        setResult({
          type: "danger",
          nameA: itemA.ITEM_NAME,
          nameB: itemB.ITEM_NAME,
          content: durRes.warnings?.[0]?.PROHBT_CONTENT || "병용금기 약물입니다. 함께 복용하지 마세요.",
          aiAnswer: aiRes.answer || null,
        });
      } else {
        setResult({
          type: "safe",
          nameA: itemA.ITEM_NAME,
          nameB: itemB.ITEM_NAME,
          content: "현재 DB에서 이 두 약의 병용금기 정보가 확인되지 않았습니다. 그러나 반드시 의사·약사와 상담하세요.",
          aiAnswer: null,
        });
      }
    } catch (e) {
      setResult({ type: "unknown", nameA: drugA, nameB: drugB, content: "서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.", aiAnswer: null });
    } finally {
      setLoading(false);
    }
  };

  const getLiquidColor = () => {
    if (!result) return "#D3D1C7";
    if (result.type === "danger") return "#FCEBEB";
    if (result.type === "safe") return "#E1F5EE";
    return "#D3D1C7";
  };

  const getResultIcon = () => {
    if (!result) return "?";
    if (result.type === "danger") return "✕";
    if (result.type === "safe") return "✓";
    return "?";
  };

  return (
    <>
      {/* 헤더 */}
      <div className="check-header-wrap">
        <div className="check-header-card">
          <div className="check-title">이 두 약, 같이 먹어도 될까요?</div>
          <div className="check-sub">약 이름 두 가지를 입력하면 병용 가능 여부를 확인해드려요</div>
        </div>
      </div>

      {/* 메인 */}
      <div className="check-body">

        {/* 비커 영역 */}
        <div className="beaker-section">

          {/* 비커 A */}
          <div className="beaker-wrap">
            <svg className="beaker-svg" viewBox="0 0 120 150">
              <defs>
                <clipPath id="clipA">
                  <path d="M32 10 L32 80 L8 130 Q5 138 14 138 L106 138 Q115 138 112 130 L88 80 L88 10 Z"/>
                </clipPath>
              </defs>
              {/* 비커 몸체 */}
              <path d="M32 10 L32 80 L8 130 Q5 138 14 138 L106 138 Q115 138 112 130 L88 80 L88 10 Z"
                fill="rgba(255,255,255,0.15)" stroke="#9FE1CB" strokeWidth="2.5" strokeLinejoin="round"/>
              <line x1="26" y1="10" x2="94" y2="10" stroke="#9FE1CB" strokeWidth="2.5" strokeLinecap="round"/>
              {/* 액체 */}
              <rect x="0" y="95" width="120" height="60" fill="#E1F5EE" opacity="0.6" clipPath="url(#clipA)"/>
              {/* 약 이름 */}
              <text x="60" y="125" textAnchor="middle" fontSize="10" fill="#0F6E56" fontFamily="inherit">
                {drugA ? (drugA.length > 7 ? drugA.slice(0, 7) + "..." : drugA) : "약 이름"}
              </text>
              {/* A 라벨 */}
              <text x="60" y="28" textAnchor="middle" fontSize="13" fontWeight="500" fill="#1D9E75" fontFamily="inherit">A</text>
            </svg>
            <input
              className="beaker-input"
              type="text"
              value={drugA}
              onChange={e => setDrugA(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleCheck()}
              placeholder="첫 번째 약 이름"
            />
          </div>

          {/* 플러스 */}
          <div className="plus-sign">+</div>

          {/* 비커 B */}
          <div className="beaker-wrap">
            <svg className="beaker-svg" viewBox="0 0 120 150">
              <defs>
                <clipPath id="clipB">
                  <path d="M32 10 L32 80 L8 130 Q5 138 14 138 L106 138 Q115 138 112 130 L88 80 L88 10 Z"/>
                </clipPath>
              </defs>
              <path d="M32 10 L32 80 L8 130 Q5 138 14 138 L106 138 Q115 138 112 130 L88 80 L88 10 Z"
                fill="rgba(255,255,255,0.15)" stroke="#B5D4F4" strokeWidth="2.5" strokeLinejoin="round"/>
              <line x1="26" y1="10" x2="94" y2="10" stroke="#B5D4F4" strokeWidth="2.5" strokeLinecap="round"/>
              <rect x="0" y="95" width="120" height="60" fill="#E6F1FB" opacity="0.6" clipPath="url(#clipB)"/>
              <text x="60" y="125" textAnchor="middle" fontSize="10" fill="#185FA5" fontFamily="inherit">
                {drugB ? (drugB.length > 7 ? drugB.slice(0, 7) + "..." : drugB) : "약 이름"}
              </text>
              <text x="60" y="28" textAnchor="middle" fontSize="13" fontWeight="500" fill="#378ADD" fontFamily="inherit">B</text>
            </svg>
            <input
              className="beaker-input"
              type="text"
              value={drugB}
              onChange={e => setDrugB(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleCheck()}
              placeholder="두 번째 약 이름"
            />
          </div>

          {/* 화살표 */}
          <div className="arrow-sign">→</div>

          {/* 결과 비커 */}
          <div className="beaker-wrap">
            <svg className="beaker-svg" viewBox="0 0 120 150">
              <defs>
                <clipPath id="clipR">
                  <path d="M32 10 L32 80 L8 130 Q5 138 14 138 L106 138 Q115 138 112 130 L88 80 L88 10 Z"/>
                </clipPath>
              </defs>
              <path d="M32 10 L32 80 L8 130 Q5 138 14 138 L106 138 Q115 138 112 130 L88 80 L88 10 Z"
                fill="rgba(255,255,255,0.15)" stroke="#D3D1C7" strokeWidth="2.5" strokeLinejoin="round"/>
              <line x1="26" y1="10" x2="94" y2="10" stroke="#D3D1C7" strokeWidth="2.5" strokeLinecap="round"/>
              <rect x="0" y="80" width="120" height="75" fill={getLiquidColor()} opacity="0.7" clipPath="url(#clipR)"/>
              <text x="60" y="122" textAnchor="middle" fontSize="26" fontFamily="inherit"
                fill={result?.type === "danger" ? "#E24B4A" : result?.type === "safe" ? "#1D9E75" : "#888780"}>
                {loading ? "..." : getResultIcon()}
              </text>
            </svg>
            <span className="beaker-label">결과</span>
          </div>
        </div>

        {/* 확인 버튼 */}
        <div className="check-btn-wrap">
          <button className="check-btn" onClick={handleCheck} disabled={loading}>
            {loading ? "확인 중..." : "병용 가능 여부 확인하기"}
          </button>
        </div>

        {/* 결과 카드 */}
        {result && (
          <div className={`result-card ${result.type}`}>
            <div className="result-card-header">
              <div className={`result-badge ${result.type}`}>
                {result.type === "danger" ? "!" : result.type === "safe" ? "✓" : "?"}
              </div>
              <div>
                <div className={`result-title ${result.type}`}>
                  {result.type === "danger" && "병용 주의 — 함께 복용하지 마세요"}
                  {result.type === "safe" && "병용금기 정보 없음"}
                  {result.type === "unknown" && "확인 불가"}
                </div>
                <div className="result-drug-names">{result.nameA} + {result.nameB}</div>
              </div>
            </div>
            <div className="result-content">{result.content}</div>
            {result.aiAnswer && (
              <div className="ai-answer-box">
                <div className="ai-answer-label">AI 상세 분석</div>
                <p className="ai-answer-text">{result.aiAnswer}</p>
              </div>
            )}
            <div className="result-footer">
              ※ 본 정보는 식약처 DUR 공식 데이터 기반이며, 참고용입니다. 반드시 의사·약사와 상담하세요.
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default CheckPage;
