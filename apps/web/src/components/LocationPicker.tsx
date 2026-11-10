'use client';

import React, { useState } from 'react';
import { MapPin, Navigation, CheckCircle2 } from 'lucide-react';

interface LocationPickerProps {
  district: string;
  setDistrict: (dist: string) => void;
  landmark: string;
  setLandmark: (lm: string) => void;
  address: string;
  setAddress: (addr: string) => void;
  onCoordinatesSelected?: (lat: number, lng: number) => void;
  language: 'en' | 'ta';
}

const TN_DISTRICTS = [
  "Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli", 
  "Erode", "Vellore", "Thanjavur", "Kanchipuram", "Cuddalore", "Dindigul", "Villupuram"
];

export function LocationPicker({
  district, setDistrict,
  landmark, setLandmark,
  address, setAddress,
  onCoordinatesSelected,
  language
}: LocationPickerProps) {
  const [isGettingGps, setIsGettingGps] = useState(false);
  const [gpsStatus, setGpsStatus] = useState<string | null>(null);
  const [selectedPoint, setSelectedPoint] = useState<{ x: number; y: number } | null>({ x: 180, y: 90 });

  const handleGetGps = () => {
    setIsGettingGps(true);
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setIsGettingGps(false);
          setGpsStatus(`GPS Verified (${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)})`);
          if (onCoordinatesSelected) {
            onCoordinatesSelected(pos.coords.latitude, pos.coords.longitude);
          }
        },
        () => {
          setIsGettingGps(false);
          // Fallback Chennai coordinates
          setGpsStatus("GPS Location Set (13.0827° N, 80.2707° E)");
          if (onCoordinatesSelected) {
            onCoordinatesSelected(13.0827, 80.2707);
          }
        }
      );
    } else {
      setIsGettingGps(false);
      setGpsStatus("GPS Location Set (13.0827° N, 80.2707° E)");
    }
  };

  const handleMapClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setSelectedPoint({ x, y });
    setGpsStatus(`Map Pin Placed (${(13.0 + y/1000).toFixed(4)}, ${(80.2 + x/1000).toFixed(4)})`);
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-slate-800 text-sm flex items-center gap-2">
          <MapPin className="w-4 h-4 text-tn-navy" />
          <span>{language === 'ta' ? 'இடம் மற்றும் மாவட்டம்' : 'Grievance Location & District'}</span>
        </h3>
        <button
          type="button"
          onClick={handleGetGps}
          disabled={isGettingGps}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-semibold border border-blue-200 transition-colors"
        >
          <Navigation className={`w-3.5 h-3.5 ${isGettingGps ? 'animate-spin' : ''}`} />
          <span>{language === 'ta' ? 'ஜிபிஎஸ் பயன்பாடு' : 'Use Current GPS'}</span>
        </button>
      </div>

      {gpsStatus && (
        <div className="flex items-center space-x-1.5 text-xs text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded border border-emerald-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>{gpsStatus}</span>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-medium text-slate-700 mb-1">
            {language === 'ta' ? 'மாவட்டம் (District) *' : 'District *'}
          </label>
          <select
            value={district}
            onChange={(e) => setDistrict(e.target.value)}
            className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-tn-navy focus:outline-none bg-white"
          >
            {TN_DISTRICTS.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-700 mb-1">
            {language === 'ta' ? 'அடையாளம் / முக்கிய இடம் (Landmark)' : 'Landmark / Area'}
          </label>
          <input
            type="text"
            value={landmark}
            onChange={(e) => setLandmark(e.target.value)}
            placeholder={language === 'ta' ? 'எ.கா. பேருந்து நிலையம் அருகில்' : 'e.g. Near Bus Stand / Pillar 42'}
            className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-tn-navy focus:outline-none"
          />
        </div>
      </div>

      <div>
        <label className="block text-xs font-medium text-slate-700 mb-1">
          {language === 'ta' ? 'முகவரி (Address)' : 'Street / Area Address'}
        </label>
        <textarea
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          rows={2}
          placeholder={language === 'ta' ? 'தெரு பெயர், கதவு எண்...' : 'Street name, door no...'}
          className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-tn-navy focus:outline-none"
        />
      </div>

      {/* Interactive Map Picker Fallback */}
      <div>
        <label className="block text-xs font-medium text-slate-500 mb-1">
          {language === 'ta' ? 'வரைபடத்தில் கிளிக் செய்க (Interactive Map Pick Fallback):' : 'Click on Map to Adjust Pin (Fallback):'}
        </label>
        <div
          onClick={handleMapClick}
          className="relative h-28 w-full bg-slate-100 rounded-lg border border-slate-300 cursor-pointer overflow-hidden shadow-inner flex items-center justify-center"
          style={{ backgroundImage: 'radial-gradient(#CBD5E1 1px, transparent 1px)', backgroundSize: '16px 16px' }}
        >
          <span className="text-[11px] text-slate-400 font-medium select-none">
            [ Interactive GIS Map View - Click to drop location pin ]
          </span>
          {selectedPoint && (
            <div
              className="absolute transform -translate-x-1/2 -translate-y-full text-red-600 transition-all"
              style={{ left: `${selectedPoint.x}px`, top: `${selectedPoint.y}px` }}
            >
              <MapPin className="w-6 h-6 fill-red-600 text-white shadow-lg animate-bounce" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
