'use client';

import { useState } from 'react';
import { Sparkles, Send, Loader2, ExternalLink, FileText, CheckSquare, X } from 'lucide-react';

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Modal State
  const [modalType, setModalType] = useState<'pitch' | 'plan' | null>(null);
  const [modalLoading, setModalLoading] = useState(false);
  const [modalData, setModalData] = useState<any>(null);

  const [profile, setProfile] = useState({
    id: 'std_101',
    name: 'Alex Johnson',
    education_level: 'B.Tech 3rd year',
    degree: 'B.Tech',
    major: 'Computer Science',
    field_of_study: 'Computer Science',
    graduation_year: 2027,
    cgpa: 8.5,
    skills: 'Python, React, Machine Learning',
    interests: 'AI research, Web Development',
    location: 'India',
    eligibility_notes: 'Graduating 2027',
  });

  const [rawText, setRawText] = useState(
    'Software Engineering Intern - Summer 2027 at Google. Must be pursuing B.Tech/B.E in CS. Minimum CGPA 7.0. Location: Bangalore / Remote. Applicants must be graduating in 2026 or 2027.'
  );

  const getFormattedProfile = () => ({
    id: profile.id || 'std_101',
    name: profile.name || 'Alex Johnson',
    degree: profile.degree || profile.education_level || 'B.Tech',
    major: profile.major || profile.field_of_study || 'Computer Science',
    graduation_year: profile.graduation_year ? parseInt(profile.graduation_year as any, 10) : 2027,
    education_level: profile.education_level,
    field_of_study: profile.field_of_study,
    cgpa: profile.cgpa ? parseFloat(profile.cgpa as any) : 8.5,
    skills: profile.skills ? profile.skills.split(',').map((s) => s.trim()).filter(Boolean) : ['Python', 'React'],
    interests: profile.interests ? profile.interests.split(',').map((i) => i.trim()).filter(Boolean) : ['AI research'],
    location: profile.location || 'India',
    eligibility_notes: profile.eligibility_notes || 'Graduating 2027',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResults([]);
    setError(null);

    const payload = {
      profile: getFormattedProfile(),
      raw_listings: [{ raw_text: rawText, source_url: 'https://careers.google.com' }],
    };

    try {
      const response = await fetch('http://127.0.0.1:8000/api/pipeline/rank', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail?.[0]?.msg || 'Validation failed');
      }

      const data = await response.json();
      const rankedItems = data.ranked_results || data.items || data.results || (Array.isArray(data) ? data : [data]);
      setResults(rankedItems);
    } catch (err: any) {
      setError(err.message || 'Error processing request.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunDemo = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://127.0.0.1:8000/api/demo/run-sample');
      if (!response.ok) throw new Error('Demo request failed');
      const data = await response.json();
      const rankedItems = data.result?.ranked_results || data.result?.items || data.result || [];
      setResults(Array.isArray(rankedItems) ? rankedItems : [rankedItems]);
    } catch (err: any) {
      setError('Error running sample demo data.');
    } finally {
      setLoading(false);
    }
  };

  // Helper to standardise opportunity structure for API calls
  const extractOpportunityData = (item: any) => {
    const opp = item.opportunity || item.extracted || item;
    return {
      id: opp.id || 'opp_101',
      title: opp.title || 'Software Engineering Opportunity',
      organization: opp.organization || 'Featured Partner',
      category: opp.category || 'internship',
      location: opp.location || 'Remote',
      is_remote: opp.is_remote ?? true,
      deadline: opp.deadline || '2026-12-31',
      eligibility: opp.eligibility || {
        min_gpa: 3.0,
        allowed_majors: [profile.major || 'Computer Science'],
        graduation_years: [2027],
        target_degrees: ['B.Tech', 'B.S.'],
        location_requirement: 'Remote',
        work_authorization: [],
      },
      required_skills: opp.required_skills || (profile.skills ? profile.skills.split(',').map((s) => s.trim()) : []),
      tags: opp.tags || ['Tech'],
      summary: opp.summary || 'Opportunity summary',
      apply_url: opp.apply_url || 'https://careers.google.com',
      extraction_confidence: opp.extraction_confidence || 0.9,
    };
  };

  // Handler for Pitch Generation
  const handleGeneratePitch = async (item: any) => {
    setModalType('pitch');
    setModalLoading(true);
    setModalData(null);

    const formattedProfile = getFormattedProfile();
    const formattedOpp = extractOpportunityData(item);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/tailor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile: formattedProfile,
          opportunity: formattedOpp,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail?.[0]?.msg || 'Failed to generate pitch');
      }
      setModalData(data);
    } catch (err: any) {
      setModalData({ error: err.message || 'Failed to generate tailored pitch.' });
    } finally {
      setModalLoading(false);
    }
  };

  // Handler for Action Plan Generation
  const handleGeneratePlan = async (item: any) => {
    setModalType('plan');
    setModalLoading(true);
    setModalData(null);

    const formattedProfile = getFormattedProfile();
    const formattedOpp = extractOpportunityData(item);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/action-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile: formattedProfile,
          opportunity: formattedOpp,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail?.[0]?.msg || 'Failed to generate action plan');
      }
      setModalData(data);
    } catch (err: any) {
      setModalData({ error: err.message || 'Failed to generate action plan.' });
    } finally {
      setModalLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8 font-sans relative">
      <header className="max-w-6xl mx-auto mb-8 flex items-center justify-between border-b border-slate-800 pb-4">
        <h1 className="text-2xl font-bold flex items-center gap-2 text-indigo-400">
          <Sparkles className="w-6 h-6" /> Opp.ai — Opportunity Agent
        </h1>
        <button
          onClick={handleRunDemo}
          type="button"
          className="text-xs bg-indigo-500/20 text-indigo-300 hover:bg-indigo-500/30 border border-indigo-500/40 px-3 py-1.5 rounded-full transition"
        >
          ⚡ Run Live Demo Data
        </button>
      </header>

      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
        <form onSubmit={handleSubmit} className="space-y-6 bg-slate-800/50 border border-slate-700/50 p-6 rounded-xl">
          <h2 className="text-lg font-semibold text-white">1. Student Profile</h2>

          <div>
            <label className="block text-xs text-slate-400 mb-1">Student Name</label>
            <input
              type="text"
              value={profile.name}
              onChange={(e) => setProfile({ ...profile, name: e.target.value })}
              className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm text-white"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Degree</label>
              <input
                type="text"
                value={profile.degree}
                onChange={(e) => setProfile({ ...profile, degree: e.target.value, education_level: e.target.value })}
                className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm text-white"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Major</label>
              <input
                type="text"
                value={profile.major}
                onChange={(e) => setProfile({ ...profile, major: e.target.value, field_of_study: e.target.value })}
                className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm text-white"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Graduation Year</label>
              <input
                type="number"
                value={profile.graduation_year}
                onChange={(e) => setProfile({ ...profile, graduation_year: parseInt(e.target.value, 10) || 2027 })}
                className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm text-white"
              />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">CGPA / GPA</label>
              <input
                type="number"
                step="0.1"
                value={profile.cgpa}
                onChange={(e) => setProfile({ ...profile, cgpa: e.target.value as any })}
                className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm text-white"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs text-slate-400 mb-1">Location</label>
            <input
              type="text"
              value={profile.location}
              onChange={(e) => setProfile({ ...profile, location: e.target.value })}
              className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm text-white"
            />
          </div>

          <div>
            <label className="block text-xs text-slate-400 mb-1">Skills (comma separated)</label>
            <input
              type="text"
              value={profile.skills}
              onChange={(e) => setProfile({ ...profile, skills: e.target.value })}
              className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm text-white"
            />
          </div>

          <h2 className="text-lg font-semibold text-white pt-4 border-t border-slate-700">2. Raw Listing Input</h2>

          <div>
            <label className="block text-xs text-slate-400 mb-1">Paste Raw Listing Text</label>
            <textarea
              rows={4}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-sm text-white"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2.5 rounded-lg transition flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-4 h-4" />}
            Extract, Match & Rank Listing
          </button>
        </form>

        <div className="space-y-6">
          <h2 className="text-lg font-semibold text-white">3. Ranked Opportunities Feed</h2>

          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-300 text-sm">
              <strong>Error:</strong> {error}
            </div>
          )}

          {!results.length && !loading && !error && (
            <div className="border border-dashed border-slate-800 rounded-xl p-12 text-center text-slate-500">
              Submit a listing or click "Run Live Demo Data" above.
            </div>
          )}

          <div className="space-y-4">
            {results.map((item: any, idx: number) => {
              const opp = item.opportunity || item.extracted || item;
              const score = item.scoring_result || item.score || item;

              const title = opp.title || 'Software Engineering Opportunity';
              const org = opp.organization || 'Featured Partner';
              const category = opp.category || 'internship';
              const summary = opp.summary || opp.description || 'Structured details extracted via AI agent.';
              const location = opp.location || 'Remote / Hybrid';
              const tags = opp.tags || [];

              const relScore = score.relevance_score ?? score.score ?? 85;
              const fit = score.eligibility_fit ?? score.fit ?? 'eligible';
              const reasoning = score.reasoning || score.explanation;

              return (
                <div key={idx} className="bg-slate-800/80 border border-slate-700 rounded-xl p-6 space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-700 pb-3">
                    <span className="text-xs font-semibold px-2.5 py-1 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase">
                      {category}
                    </span>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-slate-400">
                        Score: <strong className="text-indigo-400 text-sm">{relScore}/100</strong>
                      </span>
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                        {fit}
                      </span>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-bold text-white flex items-center justify-between">
                      {title}
                      {opp.source_url && (
                        <a href={opp.source_url} target="_blank" rel="noreferrer" className="text-indigo-400 hover:text-indigo-300">
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      )}
                    </h3>
                    <p className="text-xs text-slate-400">{org} • {location}</p>
                  </div>

                  <p className="text-sm text-slate-300">{summary}</p>

                  {reasoning && (
                    <div className="bg-slate-900/60 p-3 rounded-lg border border-slate-800/80 text-xs text-slate-300">
                      <strong className="text-indigo-300">AI Match Assessment: </strong> {reasoning}
                    </div>
                  )}

                  {tags.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {tags.map((tag: string, tIdx: number) => (
                        <span key={tIdx} className="bg-slate-700/60 text-slate-300 text-xs px-2 py-0.5 rounded">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Action Buttons for Pitch and Action Plan */}
                  <div className="flex gap-3 pt-2 border-t border-slate-700/60">
                    <button
                      type="button"
                      onClick={() => handleGeneratePitch(item)}
                      className="flex-1 bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 text-xs font-medium py-2 rounded-lg transition flex items-center justify-center gap-1.5"
                    >
                      <FileText className="w-3.5 h-3.5" /> Generate Pitch
                    </button>
                    <button
                      type="button"
                      onClick={() => handleGeneratePlan(item)}
                      className="flex-1 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 text-xs font-medium py-2 rounded-lg transition flex items-center justify-center gap-1.5"
                    >
                      <CheckSquare className="w-3.5 h-3.5" /> Action Plan
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Modal Overlay for Pitch / Action Plan Output */}
      {modalType && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-800 border border-slate-700 rounded-xl max-w-2xl w-full p-6 space-y-4 max-h-[85vh] overflow-y-auto relative">
            <button
              onClick={() => setModalType(null)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              {modalType === 'pitch' ? (
                <>
                  <FileText className="w-5 h-5 text-indigo-400" /> Tailored Application Pitch
                </>
              ) : (
                <>
                  <CheckSquare className="w-5 h-5 text-emerald-400" /> Application Action Plan
                </>
              )}
            </h3>

            {modalLoading ? (
              <div className="py-12 flex flex-col items-center justify-center gap-3 text-slate-400">
                <Loader2 className="w-8 h-8 animate-spin text-indigo-400" />
                <p className="text-sm">Generating tailored response with AI agent...</p>
              </div>
            ) : modalData?.error ? (
              <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-300 text-sm">
                {modalData.error}
              </div>
            ) : (
              <div className="space-y-4 text-sm text-slate-300 pt-2">
                {modalType === 'pitch' && modalData && (
                  <>
                    <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-700 space-y-2">
                      <h4 className="text-xs font-semibold text-indigo-400 uppercase">Elevator Pitch</h4>
                      <p>{modalData.elevator_pitch || modalData.pitch || JSON.stringify(modalData)}</p>
                    </div>
                    {modalData.key_talking_points && (
                      <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-700 space-y-2">
                        <h4 className="text-xs font-semibold text-indigo-400 uppercase">Key Strengths & Talking Points</h4>
                        <ul className="list-disc pl-5 space-y-1">
                          {Array.isArray(modalData.key_talking_points) ? (
                            modalData.key_talking_points.map((pt: string, i: number) => <li key={i}>{pt}</li>)
                          ) : (
                            <li>{modalData.key_talking_points}</li>
                          )}
                        </ul>
                      </div>
                    )}
                  </>
                )}

                {modalType === 'plan' && modalData && (
                  <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-700 space-y-3">
                    <h4 className="text-xs font-semibold text-emerald-400 uppercase">Step-by-Step Action Items</h4>
                    {modalData.checklist || modalData.steps ? (
                      <ul className="space-y-2">
                        {(modalData.checklist || modalData.steps).map((step: any, i: number) => (
                          <li key={i} className="flex items-start gap-2 border-b border-slate-800 pb-2">
                            <span className="text-emerald-400 text-xs font-bold mt-0.5">{i + 1}.</span>
                            <div>
                              <p className="font-medium text-white">{step.task || step.title || step}</p>
                              {step.deadline && <p className="text-xs text-slate-400">Due: {step.deadline}</p>}
                            </div>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <pre className="text-xs overflow-x-auto">{JSON.stringify(modalData, null, 2)}</pre>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
} 