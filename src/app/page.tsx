'use client';

import React from 'react';
import dynamic from 'next/dynamic';

// 클라이언트 전용 컴포넌트로 ChemicalFilter 불러오기
const ChemicalFilter = dynamic(() => import('./components/ChemicalFilter'), {
  ssr: false, // 서버 사이드 렌더링 비활성화
});

export default function Page() {
  return (
    <main className="p-4 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">화학물질 검색</h1>
      <ChemicalFilter />
    </main>
  );
}
