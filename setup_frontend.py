"""
MediLink 프론트엔드 셋업 스크립트
실행: python setup_frontend.py
pill-ai 폴더 안에 frontend 폴더와 모든 파일을 생성합니다.
"""
import os

BASE = "frontend/src"

files = {}

# ============================================================
# main.jsx (BrowserRouter 포함)
# ============================================================
files["main.jsx"] = """\
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
"""

# ============================================================
# index.css
# ============================================================
files["index.css"] = """\
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Noto Sans KR', sans-serif; }
"""

# ============================================================
# App.jsx
# ============================================================
files["App.jsx"] = """\
import { Route, Routes } from "react-router-dom";
import "./App.css";
import Main from "./pill_ai/main.jsx";
import LandingPage from "./pill_ai/pages/landing/LandingPage.jsx";
import HomePage from "./pill_ai/pages/home/HomePage.jsx";
import SearchPage from "./pill_ai/pages/search/SearchPage.jsx";

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/app" element={<Main />}>
          <Route index element={<HomePage />} />
          <Route path="home" element={<HomePage />} />
          <Route path="search" element={<SearchPage />} />
        </Route>
      </Routes>
    </>
  );
}

export default App;
"""

# ============================================================
# App.css
# ============================================================
files["App.css"] = """\
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:        #FDF0F3;
  --white:     #FFFFFF;
  --bg2:       #F5F5F5;
  --border:    #E2E2E2;
  --border-lt: #ECECEC;
  --txt1:      #1E1E1E;
  --txt2:      #6B6B6B;
  --txt3:      #A8A8A8;
  --green6:    #1D9E75;
  --green7:    #0F6E56;
  --green8:    #085041;
  --green5:    #E1F5EE;
  --green2:    #5DCAA5;
  --green1:    #9FE1CB;
  --red5:      #FCEBEB;
  --red1:      #F7C1C1;
  --red6:      #E24B4A;
  --red7:      #A32D2D;
  --amb5:      #FAEEDA;
  --amb1:      #FAC775;
  --amb6:      #EF9F27;
  --amb7:      #854F0B;
  --blue5:     #E6F1FB;
  --blue6:     #378ADD;
  --blue7:     #185FA5;
  --pink6:     #D4537E;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --pad:       32px;
}

body {
  font-family: 'Noto Sans KR', sans-serif;
  background: #f0f0f0;
}
"""

# ============================================================
# pill_ai/main.jsx (사이드바 레이아웃)
# ============================================================
files["pill_ai/main.jsx"] = """\
import React from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import "./main.css";

const Main = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const isActive = (path) => location.pathname === path;

  return (
    <div className="app-wrap">
      <div className="app">
        <nav className="sidebar">
          <div className="logo">
            <div className="logo-icon"></div>
            <span className="logo-text">MediLink</span>
          </div>
          <div className="nav">
            <div className="nav-label">메인</div>
            <div className={`nav-item ${isActive("/app") || isActive("/app/home") ? "active" : ""}`} onClick={() => navigate("/app/home")}>
              <div className="nav-dot"></div>홈
            </div>
            <div className={`nav-item ${isActive("/app/search") ? "active" : ""}`} onClick={() => navigate("/app/search")}>
              <div className="nav-dot"></div>검색
            </div>
            <div className="nav-item">
              <div className="nav-dot"></div>내 약함
            </div>
            <div className="nav-label">알림</div>
            <div className="nav-item">
              <div className="nav-dot"></div>알림
              <span className="nav-badge">1</span>
            </div>
            <div className="nav-label">기타</div>
            <div className="nav-item">
              <div className="nav-dot"></div>의료진 공유
            </div>
            <div className="nav-item">
              <div className="nav-dot"></div>설정
            </div>
          </div>
          <div className="sidebar-footer">
            <div className="avatar">민지</div>
            <div>
              <div className="user-name">김민지</div>
              <div className="user-role">일반 사용자</div>
            </div>
          </div>
        </nav>
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Main;
"""

# ============================================================
# pill_ai/main.css
# ============================================================
files["pill_ai/main.css"] = """\
.app-wrap {
  display: flex;
  justify-content: center;
  padding: 40px 20px;
  min-height: 100vh;
  background: #f0f0f0;
}
.app {
  display: flex;
  width: 1200px;
  height: 720px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 40px rgba(0,0,0,.12);
  background: var(--white);
}
.sidebar {
  width: 220px;
  flex-shrink: 0;
  background: var(--white);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 20px 0;
}
.logo { display: flex; align-items: center; gap: 9px; padding: 0 20px 24px; }
.logo-icon {
  width: 28px; height: 28px;
  background: var(--green6); border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
}
.logo-icon::after { content: ''; width: 10px; height: 10px; background: white; border-radius: 50%; }
.logo-text { font-size: 15px; font-weight: 600; color: var(--txt1); }
.nav { flex: 1; }
.nav-label { font-size: 10px; color: var(--txt3); padding: 14px 20px 5px; letter-spacing: .07em; text-transform: uppercase; }
.nav-item { display: flex; align-items: center; gap: 10px; padding: 10px 20px; font-size: 13px; color: var(--txt2); cursor: pointer; }
.nav-item:hover { background: #fafafa; }
.nav-item.active { background: var(--green5); color: var(--green7); font-weight: 600; }
.nav-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--txt3); flex-shrink: 0; }
.nav-item.active .nav-dot { background: var(--green6); }
.nav-badge { margin-left: auto; background: var(--red6); color: white; font-size: 10px; font-weight: 600; border-radius: 10px; padding: 1px 7px; }
.sidebar-footer { padding: 14px 20px; border-top: 1px solid var(--border); display: flex; align-items: center; gap: 10px; }
.avatar { width: 32px; height: 32px; border-radius: 50%; background: var(--green1); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; color: var(--green8); flex-shrink: 0; }
.user-name { font-size: 13px; font-weight: 600; color: var(--txt1); }
.user-role { font-size: 11px; color: var(--txt3); }
.main-content { flex: 1; background: var(--bg); overflow-y: auto; display: flex; flex-direction: column; }
"""

# ============================================================
# LandingPage.jsx (로그인 전 홈화면)
# ============================================================
files["pill_ai/pages/landing/LandingPage.jsx"] = """\
import React from "react";
import { useNavigate } from "react-router-dom";
import "./LandingPage.css";

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="landing-body">
      <div className="landing-container">

        {/* 헤더 */}
        <div className="landing-header">
          <div className="landing-logo">
            <div className="landing-logo-icon"></div>
            <span className="landing-logo-text">MediLink</span>
          </div>
          <div className="landing-nav-btns">
            <button className="btn-login" onClick={() => navigate("/app/home")}>로그인</button>
            <button className="btn-signup" onClick={() => navigate("/app/home")}>회원가입</button>
          </div>
        </div>

        {/* 히어로 */}
        <div className="landing-hero">
          <div>
            <h1>내 약을 더 안전하게<br />관리하세요</h1>
            <p>
              MediLink는 복약 일정 관리, 약물 상호작용 알림,<br />
              개인 맞춤 건강 관리를 하나로 제공합니다.
            </p>
            <button className="btn-cta" onClick={() => navigate("/app/home")}>지금 시작하기</button>
          </div>
          <div className="hero-card">
            <h3>주요 기능 미리보기</h3>
            <ul>
              <li>✔ 복약 스케줄 자동 관리</li>
              <li>✔ 병용 금기 알림</li>
              <li>✔ 약 정보 검색</li>
              <li>✔ 복약 이력 기록</li>
            </ul>
          </div>
        </div>

        {/* 기능 */}
        <div className="landing-features">
          <div className="feature-card">
            <div className="feature-icon">💊</div>
            <h4>복약 관리</h4>
            <p>하루 복약 스케줄을 자동으로 관리합니다.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⚠️</div>
            <h4>안전 알림</h4>
            <p>약물 상호작용 및 주의사항을 알려줍니다.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h4>약 정보 검색</h4>
            <p>의약품 정보를 쉽게 확인할 수 있습니다.</p>
          </div>
        </div>

        {/* CTA */}
        <div className="landing-cta">
          <h2>지금 MediLink를 시작해보세요</h2>
          <p>간편한 회원가입으로 바로 이용할 수 있습니다.</p>
          <button onClick={() => navigate("/app/home")}>회원가입</button>
        </div>

      </div>
    </div>
  );
};

export default LandingPage;
"""

# ============================================================
# LandingPage.css
# ============================================================
files["pill_ai/pages/landing/LandingPage.css"] = """\
.landing-body {
  font-family: 'Noto Sans KR', sans-serif;
  background: #FDF0F3;
  color: #1E1E1E;
  min-height: 100vh;
}
.landing-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

/* 헤더 */
.landing-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 60px;
}
.landing-logo { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 18px; }
.landing-logo-icon {
  width: 30px; height: 30px;
  background: #1D9E75; border-radius: 8px;
}
.landing-logo-text { font-size: 18px; font-weight: 700; color: #1E1E1E; }
.landing-nav-btns button {
  margin-left: 10px; padding: 8px 16px;
  border-radius: 8px; border: none; cursor: pointer; font-weight: 500;
  font-family: inherit; font-size: 14px;
}
.btn-login { background: #fff; border: 1px solid #ddd !important; color: #1E1E1E; }
.btn-signup { background: #1D9E75; color: #fff; }

/* 히어로 */
.landing-hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: 40px;
  margin-bottom: 80px;
}
.landing-hero h1 { font-size: 40px; margin-bottom: 20px; line-height: 1.3; }
.landing-hero p { color: #6B6B6B; margin-bottom: 30px; line-height: 1.6; }
.btn-cta {
  padding: 14px 26px; border: none; border-radius: 10px;
  background: #1D9E75; color: #fff; font-size: 16px;
  cursor: pointer; font-family: inherit; font-weight: 600;
}

.hero-card {
  background: #fff; padding: 30px;
  border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}
.hero-card h3 { margin-bottom: 15px; font-size: 16px; }
.hero-card ul { list-style: none; }
.hero-card li { padding: 10px 0; border-bottom: 1px solid #eee; font-size: 14px; }
.hero-card li:last-child { border-bottom: none; }

/* 기능 */
.landing-features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 80px;
}
.feature-card {
  background: #fff; padding: 24px;
  border-radius: 14px; border: 1px solid #eee;
}
.feature-icon { font-size: 28px; margin-bottom: 12px; }
.feature-card h4 { margin-bottom: 8px; font-size: 15px; }
.feature-card p { font-size: 13px; color: #6B6B6B; line-height: 1.6; }

/* CTA */
.landing-cta {
  text-align: center;
  background: #1D9E75; color: #fff;
  padding: 50px 20px; border-radius: 16px;
}
.landing-cta h2 { margin-bottom: 12px; font-size: 24px; }
.landing-cta p { font-size: 14px; opacity: 0.85; }
.landing-cta button {
  margin-top: 20px; padding: 12px 28px;
  border: none; border-radius: 10px;
  background: #fff; color: #1D9E75;
  cursor: pointer; font-size: 15px;
  font-weight: 600; font-family: inherit;
}
"""

# ============================================================
# HomePage.jsx
# ============================================================
files["pill_ai/pages/home/HomePage.jsx"] = """\
import React from "react";
import { useNavigate } from "react-router-dom";
import "./HomePage.css";

const HomePage = () => {
  const navigate = useNavigate();
  const today = new Date().toLocaleDateString("ko-KR", {
    year: "numeric", month: "long", day: "numeric", weekday: "long"
  });

  return (
    <>
      <div className="topbar">
        <div>
          <div className="greeting-title">안녕하세요, 민지님!</div>
          <div className="greeting-sub">오늘의 복약 일정을 확인하세요</div>
        </div>
        <div className="topbar-right">
          <span className="date-chip">{today}</span>
          <div className="notif-btn">
            <svg viewBox="0 0 16 16" stroke="currentColor" fill="none" strokeWidth="1.2">
              <path d="M8 2C5.8 2 4 3.8 4 6v3l-1.5 1.5h11L12 9V6c0-2.2-1.8-4-4-4Z"/>
              <path d="M6.3 11c0 .9.8 1.7 1.7 1.7s1.7-.8 1.7-1.7"/>
            </svg>
            <div className="notif-dot"></div>
          </div>
        </div>
      </div>

      <div className="content">
        <div className="stat-grid">
          <div className="stat-card green">
            <div className="stat-label">오늘 복약 완료</div>
            <div className="stat-value">2 / 3</div>
            <div className="stat-sub">아침 완료 · 점심 예정</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">복용 중인 약</div>
            <div className="stat-value">4</div>
            <div className="stat-sub">약 3종 · 건기식 1종</div>
          </div>
          <div className="stat-card red">
            <div className="stat-label">경고 알림</div>
            <div className="stat-value">1</div>
            <div className="stat-sub">병용금기 확인 필요</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">이번 주 복약률</div>
            <div className="stat-value">87%</div>
            <div className="stat-sub">지난 주보다 +5%</div>
          </div>
        </div>

        <div className="two-col">
          <div className="left-col">
            <div className="section-card">
              <div className="section-head">
                <span className="section-title">오늘 복약 타임라인</span>
                <a className="section-link" href="#">전체 보기</a>
              </div>
              <div className="tl-item">
                <span className="tl-time">08:00</span>
                <div className="tl-dot done"></div>
                <div className="tl-info">
                  <div className="tl-name">아침 복약</div>
                  <div className="tl-pills">
                    <span className="pill-tag">Tylenol ER 1정</span>
                    <span className="pill-tag">Omega-3 1캡슐</span>
                  </div>
                </div>
                <span className="tl-status done">완료</span>
              </div>
              <div className="tl-item">
                <span className="tl-time">12:30</span>
                <div className="tl-dot now"></div>
                <div className="tl-info">
                  <div className="tl-name">점심 복약</div>
                  <div className="tl-pills">
                    <span className="pill-tag">가스모틴 1정</span>
                    <span className="pill-tag">비타민 C 1정</span>
                  </div>
                </div>
                <span className="tl-status now">복용 시간</span>
              </div>
              <div className="tl-item">
                <span className="tl-time">20:00</span>
                <div className="tl-dot later"></div>
                <div className="tl-info">
                  <div className="tl-name">저녁 복약</div>
                  <div className="tl-pills">
                    <span className="pill-tag">Tylenol ER 1정</span>
                  </div>
                </div>
                <span className="tl-status later">예정</span>
              </div>
            </div>

            <div className="section-card">
              <div className="section-head">
                <span className="section-title">최근 검색한 약</span>
                <a className="section-link" href="#" onClick={(e) => { e.preventDefault(); navigate("/app/search"); }}>검색하러 가기</a>
              </div>
              <div className="recent-item" onClick={() => navigate("/app/search")}>
                <div className="drug-icon"><div className="drug-pill" style={{background:"var(--green6)"}}></div></div>
                <div><div className="recent-name">타이레놀 ER 650mg</div><div className="recent-sub">아세트아미노펜 · 일반의약품</div></div>
                <span className="recent-arr">›</span>
              </div>
              <div className="recent-item" onClick={() => navigate("/app/search")}>
                <div className="drug-icon"><div className="drug-pill" style={{background:"var(--blue6)"}}></div></div>
                <div><div className="recent-name">탁센 연질캡슐</div><div className="recent-sub">이부프로펜 · 일반의약품</div></div>
                <span className="recent-arr">›</span>
              </div>
            </div>
          </div>

          <div>
            <div className="section-card" style={{marginBottom:"14px"}}>
              <div className="section-head">
                <span className="section-title">경고 알림</span>
                <a className="section-link" href="#">전체 보기</a>
              </div>
              <div className="alert-item high">
                <div className="alert-icon">!</div>
                <div>
                  <div className="alert-label">병용금기 주의</div>
                  <div className="alert-desc">탁센 + 타이레놀 ER · 동시 복용 금지</div>
                </div>
              </div>
              <div className="alert-item med">
                <div className="alert-icon">⏱</div>
                <div>
                  <div className="alert-label">복용 간격 권고</div>
                  <div className="alert-desc">칼슘 + 철분 · 4시간 간격 권장</div>
                </div>
              </div>
            </div>

            <div className="section-card">
              <div className="section-head">
                <span className="section-title">복약 현황</span>
              </div>
              <div className="status-item">
                <div><div className="status-name">Tylenol ER</div><div className="status-ingr">아세트아미노펜 650mg</div></div>
                <div><div className="status-tag" style={{color:"var(--green6)"}}>상시 복용</div><div className="status-freq">1일 3회</div></div>
              </div>
              <div className="status-item">
                <div><div className="status-name">가스모틴</div><div className="status-ingr">모사프리드 5mg</div></div>
                <div><div className="status-tag" style={{color:"var(--green6)"}}>상시 복용</div><div className="status-freq">1일 3회</div></div>
              </div>
              <div className="status-item">
                <div><div className="status-name">Omega-3</div><div className="status-ingr">오메가-3 지방산 · 건기식</div></div>
                <div><div className="status-tag" style={{color:"var(--blue7)"}}>건강기능식품</div><div className="status-freq">1일 1회</div></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default HomePage;
"""

# ============================================================
# HomePage.css
# ============================================================
files["pill_ai/pages/home/HomePage.css"] = """\
.topbar { display: flex; align-items: center; justify-content: space-between; padding: 22px var(--pad) 0; }
.greeting-title { font-size: 18px; font-weight: 600; color: var(--txt1); }
.greeting-sub   { font-size: 13px; color: var(--txt2); margin-top: 3px; }
.topbar-right   { display: flex; align-items: center; gap: 10px; }
.date-chip { font-size: 12px; color: var(--txt2); background: var(--white); border: 1px solid var(--border); border-radius: 20px; padding: 5px 13px; }
.notif-btn { width: 34px; height: 34px; border: 1px solid var(--border); border-radius: 9px; background: var(--white); display: flex; align-items: center; justify-content: center; cursor: pointer; position: relative; color: var(--txt2); }
.notif-btn svg { width: 15px; height: 15px; }
.notif-dot { width: 7px; height: 7px; background: var(--red6); border-radius: 50%; position: absolute; top: 6px; right: 6px; border: 1.5px solid var(--bg); }
.content { padding: 20px var(--pad) 28px; flex: 1; }
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
.stat-card { background: var(--white); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 14px 16px; }
.stat-card.green { background: var(--green5); border-color: var(--green1); }
.stat-card.red   { background: var(--red5);   border-color: var(--red1); }
.stat-label { font-size: 11px; color: var(--txt3); margin-bottom: 5px; }
.stat-value { font-size: 23px; font-weight: 600; color: var(--txt1); line-height: 1; }
.stat-card.green .stat-value { color: var(--green7); }
.stat-card.red   .stat-value { color: var(--red7); }
.stat-sub { font-size: 11px; color: var(--txt2); margin-top: 6px; }
.two-col { display: grid; grid-template-columns: 1fr 340px; gap: 16px; }
.left-col { display: flex; flex-direction: column; gap: 14px; }
.section-card { background: var(--white); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 18px; }
.section-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid var(--border-lt); }
.section-title { font-size: 13px; font-weight: 600; color: var(--txt2); }
.section-link  { font-size: 12px; color: var(--green6); text-decoration: none; cursor: pointer; }
.tl-item { display: flex; align-items: flex-start; gap: 10px; padding: 10px 0; border-bottom: 1px solid var(--border-lt); }
.tl-item:last-child { border-bottom: none; }
.tl-time { font-size: 12px; color: var(--txt3); width: 38px; flex-shrink: 0; padding-top: 2px; }
.tl-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; margin-top: 4px; }
.tl-dot.done  { background: var(--green6); }
.tl-dot.now   { background: var(--amb6); }
.tl-dot.later { background: var(--border); }
.tl-info { flex: 1; }
.tl-name { font-size: 13px; font-weight: 600; color: var(--txt1); }
.tl-pills { display: flex; gap: 5px; flex-wrap: wrap; margin-top: 4px; }
.pill-tag { font-size: 10px; padding: 2px 7px; background: var(--bg2); border-radius: 5px; color: var(--txt2); }
.tl-status { font-size: 12px; font-weight: 600; flex-shrink: 0; }
.tl-status.done  { color: var(--green6); }
.tl-status.now   { color: var(--amb6); }
.tl-status.later { color: var(--txt3); }
.recent-item { display: flex; align-items: center; gap: 10px; padding: 9px 10px; border-radius: var(--radius-sm); cursor: pointer; transition: background .12s; }
.recent-item:hover { background: var(--green5); }
.drug-icon { width: 32px; height: 32px; background: var(--green5); border: 1px solid var(--green1); border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.drug-pill { width: 14px; height: 8px; border-radius: 4px; }
.recent-name { font-size: 13px; font-weight: 600; color: var(--txt1); }
.recent-sub  { font-size: 11px; color: var(--txt3); margin-top: 1px; }
.recent-arr  { margin-left: auto; font-size: 16px; color: var(--txt3); }
.alert-item { display: flex; gap: 10px; padding: 11px 12px; border-radius: var(--radius-md); border: 1px solid; margin-bottom: 10px; }
.alert-item:last-child { margin-bottom: 0; }
.alert-item.high { background: var(--red5); border-color: var(--red1); }
.alert-item.med  { background: var(--amb5); border-color: var(--amb1); }
.alert-icon { width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; flex-shrink: 0; }
.alert-item.high .alert-icon { background: var(--red6); color: white; }
.alert-item.med  .alert-icon { background: var(--amb6); color: white; }
.alert-label { font-size: 12px; font-weight: 600; }
.alert-item.high .alert-label { color: var(--red7); }
.alert-item.med  .alert-label { color: var(--amb7); }
.alert-desc { font-size: 11px; color: var(--txt3); margin-top: 2px; }
.status-item { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--border-lt); }
.status-item:last-child { border-bottom: none; }
.status-name { font-size: 13px; font-weight: 600; color: var(--txt1); }
.status-ingr { font-size: 11px; color: var(--txt3); margin-top: 2px; }
.status-tag  { font-size: 11px; font-weight: 600; text-align: right; }
.status-freq { font-size: 11px; color: var(--txt3); margin-top: 2px; text-align: right; }
"""

# ============================================================
# SearchPage.jsx (API 연동)
# ============================================================
files["pill_ai/pages/search/SearchPage.jsx"] = """\
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
  const filters = ["전체", "일반의약품", "전문의약품", "건강기능식품", "성분 검색"];

  const handleSearch = async () => {
    if (!searchName.trim()) return;
    setLoading(true); setSelected(null); setAiAnswer("");
    try {
      const res = await fetch(`${API_BASE}/drug/search?name=${encodeURIComponent(searchName)}&limit=20`);
      const data = await res.json();
      setResults(data.results || []);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const handleSelect = async (item) => {
    try {
      const res = await fetch(`${API_BASE}/drug/info/${item.ITEM_SEQ}`);
      const data = await res.json();
      setSelected(data); setAiAnswer("");
    } catch (e) { setSelected(item); }
  };

  const handleAiAsk = async () => {
    if (!aiQuestion.trim() || !selected) return;
    setAiLoading(true);
    try {
      const res = await fetch(`${API_BASE}/drug/ask?question=${encodeURIComponent(aiQuestion)}&item_seq=${selected.ITEM_SEQ}&item_name=${encodeURIComponent(selected.ITEM_NAME)}`);
      const data = await res.json();
      setAiAnswer(data.answer || "답변을 가져오지 못했습니다.");
    } catch (e) { setAiAnswer("오류가 발생했습니다."); }
    finally { setAiLoading(false); }
  };

  const getOtcLabel = (code) => {
    if (!code) return "";
    if (code.includes("전문") || code === "01") return "전문의약품";
    if (code.includes("일반") || code === "02") return "일반의약품";
    return code;
  };

  return (
    <>
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
              <input className="search-input" type="text" value={searchName}
                onChange={(e) => setSearchName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                placeholder="제품명, 성분명으로 검색..." />
            </div>
            <button className="search-btn" onClick={handleSearch}>검색</button>
          </div>
          <div className="filter-row">
            {filters.map((f) => (
              <button key={f} className={`filter-chip ${filter === f ? "active" : ""}`} onClick={() => setFilter(f)}>{f}</button>
            ))}
          </div>
        </div>
      </div>

      <div className="body-wrap">
        <div className="results-card">
          <div className="result-count">
            {loading ? "검색 중..." : results.length > 0 ? `검색 결과 ${results.length}건` : "검색어를 입력하세요"}
          </div>
          {results.map((item) => (
            <div key={item.ITEM_SEQ} className={`result-item ${selected?.ITEM_SEQ === item.ITEM_SEQ ? "selected" : ""}`} onClick={() => handleSelect(item)}>
              <div className="result-top">
                <div className="drug-thumb"><div className="drug-pill-sm" style={{width:"18px",background:"var(--green6)"}}></div></div>
                <div><div className="result-name">{item.ITEM_NAME}</div><div className="result-sub">{item.ENTP_NAME}</div></div>
              </div>
              <div className="result-tags">
                <span className={`tag ${item.ETC_OTC_CODE?.includes("일반") ? "otc" : "rx"}`}>{getOtcLabel(item.ETC_OTC_CODE)}</span>
              </div>
            </div>
          ))}
        </div>

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
                    <span className={`tag ${selected.ETC_OTC_CODE?.includes("일반") ? "otc" : "rx"}`}>{getOtcLabel(selected.ETC_OTC_CODE)}</span>
                  </div>
                </div>
              </div>

              {selected.EFCY_QESITM && (
                <div className="detail-section">
                  <div className="detail-section-title">효능·효과</div>
                  <p className="detail-text">{selected.EFCY_QESITM.slice(0,300)}{selected.EFCY_QESITM.length > 300 ? "..." : ""}</p>
                </div>
              )}
              {selected.ATPN_QESITM && (
                <div className="detail-section">
                  <div className="detail-section-title">주의사항</div>
                  <div className="warn-item"><div className="warn-dot"></div><span>{selected.ATPN_QESITM.slice(0,200)}{selected.ATPN_QESITM.length > 200 ? "..." : ""}</span></div>
                </div>
              )}

              <div className="detail-section ai-section">
                <div className="detail-section-title">AI 복약 분석</div>
                <div className="ai-input-row">
                  <input className="ai-input" type="text" value={aiQuestion}
                    onChange={(e) => setAiQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleAiAsk()}
                    placeholder="예: 임산부가 먹어도 돼? / 부작용이 뭐야?" />
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
"""

# ============================================================
# SearchPage.css
# ============================================================
files["pill_ai/pages/search/SearchPage.css"] = """\
.search-header-wrap { padding: 16px var(--pad); flex-shrink: 0; }
.search-header-card { background: var(--white); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 16px 20px 14px; }
.search-title { font-size: 16px; font-weight: 600; color: var(--txt1); margin-bottom: 12px; }
.search-row { display: flex; gap: 10px; margin-bottom: 11px; }
.search-input-wrap { flex: 1; position: relative; }
.search-input { width: 100%; height: 38px; padding: 0 14px 0 38px; border: 1px solid var(--border); border-radius: var(--radius-md); font-size: 13px; font-family: inherit; background: var(--bg2); color: var(--txt1); outline: none; }
.search-input:focus { border-color: var(--green6); }
.search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--txt3); pointer-events: none; }
.search-icon svg { width: 14px; height: 14px; }
.search-btn { height: 38px; padding: 0 22px; background: var(--green6); color: white; border: none; border-radius: var(--radius-md); font-size: 13px; font-weight: 600; font-family: inherit; cursor: pointer; }
.filter-row { display: flex; gap: 7px; flex-wrap: wrap; }
.filter-chip { padding: 5px 13px; font-size: 12px; border-radius: 20px; border: 1px solid var(--border); color: var(--txt2); cursor: pointer; background: var(--white); font-family: inherit; }
.filter-chip.active { background: var(--green5); color: var(--green7); border-color: var(--green2); font-weight: 600; }
.body-wrap { flex: 1; overflow: hidden; padding: 0 var(--pad) 16px; display: flex; gap: 12px; }
.results-card { width: 320px; flex-shrink: 0; background: var(--white); border: 1px solid var(--border); border-radius: var(--radius-lg); overflow-y: auto; padding: 14px; }
.result-count { font-size: 12px; color: var(--txt3); margin-bottom: 10px; }
.result-item { padding: 12px; border-radius: var(--radius-md); border: 1px solid var(--border); background: var(--white); margin-bottom: 8px; cursor: pointer; transition: border-color .12s; }
.result-item:hover { border-color: var(--green2); }
.result-item.selected { border-color: var(--green6); background: var(--green5); }
.result-top { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.drug-thumb { width: 36px; height: 36px; border-radius: 8px; background: var(--bg2); border: 1px solid var(--border); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.drug-pill-sm { height: 10px; border-radius: 5px; }
.result-name { font-size: 13px; font-weight: 600; color: var(--txt1); }
.result-sub  { font-size: 11px; color: var(--txt3); margin-top: 2px; }
.result-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.tag { font-size: 10px; padding: 2px 8px; border-radius: 6px; }
.tag.otc { background: var(--green5); color: var(--green7); }
.tag.rx  { background: var(--blue5); color: var(--blue7); }
.detail-card { flex: 1; background: var(--white); border: 1px solid var(--border); border-radius: var(--radius-lg); overflow-y: auto; padding: 20px; }
.detail-empty { height: 100%; display: flex; align-items: center; justify-content: center; color: var(--txt3); font-size: 13px; text-align: center; line-height: 1.7; }
.detail-top { display: flex; gap: 16px; align-items: flex-start; padding-bottom: 16px; border-bottom: 1px solid var(--border-lt); margin-bottom: 16px; }
.drug-big-icon { width: 64px; height: 64px; border-radius: 12px; background: var(--green5); border: 1px solid var(--green1); display: flex; align-items: center; justify-content: center; flex-shrink: 0; overflow: hidden; }
.drug-big-icon svg { width: 36px; height: 18px; }
.detail-drug-name { font-size: 16px; font-weight: 600; color: var(--txt1); }
.detail-drug-sub  { font-size: 12px; color: var(--txt3); margin-top: 3px; }
.detail-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }
.detail-section { margin-bottom: 16px; }
.detail-section-title { font-size: 12px; font-weight: 600; color: var(--txt2); margin-bottom: 8px; text-transform: uppercase; letter-spacing: .04em; }
.detail-text { font-size: 13px; color: var(--txt1); line-height: 1.6; }
.warn-item { display: flex; align-items: flex-start; gap: 8px; padding: 9px 12px; border-radius: var(--radius-sm); background: var(--red5); border: 1px solid var(--red1); margin-bottom: 7px; }
.warn-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--red6); margin-top: 4px; flex-shrink: 0; }
.warn-item span { font-size: 12px; color: var(--red7); }
.ai-section { background: var(--bg2); border-radius: var(--radius-md); padding: 12px; }
.ai-input-row { display: flex; gap: 8px; margin-bottom: 10px; }
.ai-input { flex: 1; height: 36px; padding: 0 12px; border: 1px solid var(--border); border-radius: var(--radius-md); font-size: 12px; font-family: inherit; background: var(--white); outline: none; }
.ai-input:focus { border-color: var(--green6); }
.ai-btn { height: 36px; padding: 0 16px; background: var(--green6); color: white; border: none; border-radius: var(--radius-md); font-size: 12px; font-weight: 600; font-family: inherit; cursor: pointer; white-space: nowrap; }
.ai-btn:disabled { background: var(--txt3); cursor: not-allowed; }
.ai-answer { background: var(--white); border-radius: var(--radius-sm); padding: 10px 12px; border: 1px solid var(--border); }
.ai-answer-label { font-size: 11px; font-weight: 600; color: var(--green7); margin-bottom: 6px; }
.ai-answer p { font-size: 13px; color: var(--txt1); line-height: 1.6; }
.evidence-card { background: var(--green5); border: 1px solid var(--green1); border-radius: var(--radius-sm); padding: 10px 13px; margin-bottom: 14px; }
.evidence-label { font-size: 11px; font-weight: 600; color: var(--green7); margin-bottom: 3px; }
.evidence-desc  { font-size: 11px; color: var(--green8); }
.action-btns { display: flex; gap: 8px; padding-top: 14px; border-top: 1px solid var(--border-lt); }
.btn-add { flex: 1; height: 40px; background: var(--green6); color: white; border: none; border-radius: var(--radius-md); font-size: 13px; font-weight: 600; font-family: inherit; cursor: pointer; }
.btn-ai  { flex: 1; height: 40px; background: var(--bg2); color: var(--txt1); border: 1px solid var(--border); border-radius: var(--radius-md); font-size: 13px; font-family: inherit; cursor: pointer; }
"""

# ============================================================
# 파일 생성
# ============================================================
def create_file(rel_path, content):
    full_path = os.path.join(BASE, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ {full_path}")

if __name__ == "__main__":
    print("=" * 50)
    print("MediLink 프론트엔드 파일 생성 시작")
    print("=" * 50)

    for rel_path, content in files.items():
        create_file(rel_path, content)

    print("\n" + "=" * 50)
    print("✅ 완료! 이제 아래 명령어 실행하세요:")
    print()
    print("  cd frontend")
    print("  npm install react-router-dom")
    print("  npm run dev")
    print()
    print("브라우저에서 http://localhost:5173 접속!")
    print("=" * 50)
