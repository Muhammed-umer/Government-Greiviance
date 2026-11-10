'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../../lib/auth';
import { translations } from '../../../lib/i18n';
import { fetchApi } from '../../../lib/api';
import { VoiceRecorder } from '../../../components/VoiceRecorder';
import { LocationPicker } from '../../../components/LocationPicker';
import { FileText, Upload, Sparkles, AlertCircle, CheckCircle, ArrowRight, ArrowLeft } from 'lucide-react';

export default function NewPetitionPage() {
  const { language } = useAuth();
  const t = translations[language];
  const router = useRouter();

  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [voiceTranscript, setVoiceTranscript] = useState('');
  const [district, setDistrict] = useState('Chennai');
  const [landmark, setLandmark] = useState('');
  const [address, setAddress] = useState('');
  const [coords, setCoords] = useState<{ lat: number; lng: number } | null>(null);

  const [loading, setLoading] = useState(false);
  const [submittedPetition, setSubmittedPetition] = useState<any>(null);
  const [aiPreview, setAiPreview] = useState<{ dept: string; category: string; confidence: number; duplicateStatus: string } | null>(null);

  const handleVoiceTranscript = (text: string) => {
    setVoiceTranscript(text);
    if (!description) setDescription(text);
    if (!title) {
      setTitle(text.slice(0, 45) + '...');
    }
  };

  const handlePreviewAI = () => {
    if (!title || !description) {
      alert("Please enter title and description before proceeding.");
      return;
    }

    // Live AI Auto-route calculation preview
    let dept = "GCC";
    let category = "GARBAGE_CLEAN";
    let confidence = 0.88;
    let duplicateStatus = "New Shared Incident will be registered";

    const text = `${title} ${description}`.lower ? `${title} ${description}`.toLowerCase() : `${title} ${description}`;
    if (text.includes("wire") || text.includes("power") || text.includes("electric") || text.includes("மின்சாரம்")) {
      dept = "TANGEDCO";
      category = "ELEC_OUTAGE";
      confidence = 0.94;
    } else if (text.includes("water") || text.includes("pipe") || text.includes("குடிநீர்")) {
      dept = "CMWSSB";
      category = "WATER_LEAK";
      confidence = 0.90;
    }

    setAiPreview({ dept, category, confidence, duplicateStatus });
    setStep(3);
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const res = await fetchApi('/petitions', {
        method: 'POST',
        body: JSON.stringify({
          title,
          description: voiceTranscript ? `${description}\n\n[Voice Transcript]: ${voiceTranscript}` : description,
          language,
          address,
          landmark,
          district,
          latitude: coords?.lat,
          longitude: coords?.lng,
          voice_transcript: voiceTranscript
        })
      });
      setSubmittedPetition(res);
      setStep(4);
    } catch (err: any) {
      alert(err.message || "Submission failed. Please check login session.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-6 space-y-6">
      {/* Step Indicator */}
      <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-xs font-semibold text-slate-500">
        <span className={step >= 1 ? "text-tn-navy font-bold flex items-center gap-1" : ""}>
          1. Grievance Input
        </span>
        <span className="text-slate-300">→</span>
        <span className={step >= 2 ? "text-tn-navy font-bold flex items-center gap-1" : ""}>
          2. Location & Evidence
        </span>
        <span className="text-slate-300">→</span>
        <span className={step >= 3 ? "text-tn-navy font-bold flex items-center gap-1" : ""}>
          3. AI Auto-Route Review
        </span>
        <span className="text-slate-300">→</span>
        <span className={step === 4 ? "text-emerald-700 font-bold flex items-center gap-1" : ""}>
          4. Confirmation
        </span>
      </div>

      {step === 1 && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
          <div className="space-y-1">
            <h2 className="text-xl font-bold text-slate-800">
              {language === 'ta' ? 'புதிய குறை பதிவு செய்க' : 'Step 1: Record or Type Your Complaint'}
            </h2>
            <p className="text-xs text-slate-500">
              Record voice in Tamil/English/Tanglish or type description below.
            </p>
          </div>

          <VoiceRecorder onTranscriptReceived={handleVoiceTranscript} language={language} />

          <div className="space-y-4 pt-2">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Grievance Title *
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder={t.titlePlaceholder}
                className="w-full p-3 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-tn-navy focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Detailed Description *
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={4}
                placeholder={t.descPlaceholder}
                className="w-full p-3 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-tn-navy focus:outline-none"
              />
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              onClick={() => setStep(2)}
              disabled={!title || !description}
              className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-tn-navy hover:bg-slate-800 disabled:opacity-50 text-white font-bold text-sm shadow transition-all"
            >
              <span>Next: Location & Media</span>
              <ArrowRight className="w-4 h-4 text-amber-400" />
            </button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
          <div className="space-y-1">
            <h2 className="text-xl font-bold text-slate-800">
              Step 2: Location & Evidence Attachments
            </h2>
            <p className="text-xs text-slate-500">
              Provide exact location details and upload photo/audio/pdf proof.
            </p>
          </div>

          <LocationPicker
            district={district} setDistrict={setDistrict}
            landmark={landmark} setLandmark={setLandmark}
            address={address} setAddress={setAddress}
            onCoordinatesSelected={(lat, lng) => setCoords({ lat, lng })}
            language={language}
          />

          <div className="space-y-2 pt-2">
            <label className="block text-xs font-semibold text-slate-700">
              Attach Evidence Files (PNG, JPG, PDF, Audio max 10MB)
            </label>
            <div className="border-2 border-dashed border-slate-300 rounded-xl p-4 text-center hover:bg-slate-50 cursor-pointer">
              <Upload className="w-6 h-6 text-slate-400 mx-auto mb-1" />
              <span className="text-xs text-slate-600 font-medium">Click to choose or drag files here</span>
              <input type="file" className="hidden" multiple />
            </div>
          </div>

          <div className="flex justify-between pt-2">
            <button
              onClick={() => setStep(1)}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-slate-100 text-slate-700 font-semibold text-sm hover:bg-slate-200 transition-all"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>

            <button
              onClick={handlePreviewAI}
              className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-tn-navy hover:bg-slate-800 text-white font-bold text-sm shadow transition-all"
            >
              <span>Preview AI Auto-Routing</span>
              <Sparkles className="w-4 h-4 text-amber-400" />
            </button>
          </div>
        </div>
      )}

      {step === 3 && aiPreview && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
          <div className="space-y-1">
            <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-500" />
              <span>Step 3: Review AI Auto-Route & Duplicate Matching</span>
            </h2>
            <p className="text-xs text-slate-500">
              Verify the system routing before final submission.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-4 bg-amber-50 rounded-xl border border-amber-200 space-y-2">
              <span className="text-xs font-bold text-amber-900 uppercase tracking-wider block">
                {t.suggestedDept}
              </span>
              <p className="text-lg font-extrabold text-tn-navy">{aiPreview.dept}</p>
              <p className="text-xs text-amber-800 font-medium">Category: {aiPreview.category}</p>
              <div className="flex items-center gap-1.5 text-xs text-amber-900 font-semibold pt-1">
                <span>AI Confidence:</span>
                <span className="px-2 py-0.5 rounded bg-amber-200 font-mono">{(aiPreview.confidence * 100).toFixed(0)}%</span>
              </div>
            </div>

            <div className="p-4 bg-blue-50 rounded-xl border border-blue-200 space-y-2">
              <span className="text-xs font-bold text-blue-900 uppercase tracking-wider block">
                {t.duplicateCheck}
              </span>
              <p className="text-sm font-bold text-blue-950">{aiPreview.duplicateStatus}</p>
              <p className="text-xs text-blue-800 leading-relaxed">
                Prevents officers from working on multiple duplicate tickets for the same real-world issue.
              </p>
            </div>
          </div>

          <div className="flex justify-between pt-2">
            <button
              onClick={() => setStep(2)}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-slate-100 text-slate-700 font-semibold text-sm hover:bg-slate-200 transition-all"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>

            <button
              onClick={handleSubmit}
              disabled={loading}
              className="flex items-center space-x-2 px-8 py-3 rounded-xl bg-tn-emerald hover:bg-emerald-700 text-white font-bold text-base shadow-lg transition-all transform hover:-translate-y-0.5"
            >
              <CheckCircle className="w-5 h-5" />
              <span>{loading ? 'Submitting...' : t.submit}</span>
            </button>
          </div>
        </div>
      )}

      {step === 4 && submittedPetition && (
        <div className="bg-white rounded-2xl border border-emerald-300 p-8 shadow-xl text-center space-y-6">
          <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 mx-auto flex items-center justify-center">
            <CheckCircle className="w-10 h-10" />
          </div>

          <div className="space-y-2">
            <h2 className="text-2xl font-extrabold text-slate-900">
              {t.petitionSubmitted}
            </h2>
            <p className="text-xs text-slate-500">
              Your complaint has been registered and auto-routed to the department.
            </p>
          </div>

          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 max-w-md mx-auto space-y-1">
            <span className="text-xs text-slate-500 font-medium uppercase">{t.yourPetitionId}</span>
            <p className="text-2xl font-mono font-bold text-tn-navy tracking-wider">
              {submittedPetition.petition_number}
            </p>
          </div>

          <div className="flex justify-center gap-4 pt-4">
            <button
              onClick={() => router.push('/petition/my-petitions')}
              className="px-6 py-2.5 rounded-xl bg-tn-navy hover:bg-slate-800 text-white font-bold text-sm shadow transition-all"
            >
              View My Petitions
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
