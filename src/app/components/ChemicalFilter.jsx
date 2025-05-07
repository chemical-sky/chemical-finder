import { useState, useEffect } from 'react';

export default function ChemicalFilter() {
  const [chemicals, setChemicals] = useState([]);
  const [query, setQuery] = useState('');
  const [countryFilter, setCountryFilter] = useState('');
  const [hideReagents, setHideReagents] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [sortKey, setSortKey] = useState('chemicalName');
  const [lang, setLang] = useState('en');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    fetch('/data/registered_chemicals_enriched.json')
      .then(res => res.json())
      .then(setChemicals);
  }, []);

  const isReagent = (manufacturerList) => {
    const keywords = ["tci", "sigma", "aldrich", "santa cruz", "otto"];
    if (!Array.isArray(manufacturerList)) return false;
    return manufacturerList.some(mfg => 
      keywords.some(keyword => mfg.toLowerCase().includes(keyword))
    );
  };

  const filtered = chemicals.filter(item => {
    const matchesQuery = item.chemicalName?.toLowerCase().includes(query.toLowerCase()) ||
                         item.casNo?.replace(/-/g, '').includes(query.replace(/-/g, ''));
    const matchesCountry = countryFilter ? (
      Array.isArray(item.country) ? item.country.includes(countryFilter) : item.country === countryFilter
    ) : true;
    const reagentFiltered = hideReagents ? !isReagent(item.manufacturer) : true;
    return matchesQuery && matchesCountry && reagentFiltered;
  }).sort((a, b) => {
    const aVal = (a[sortKey] || '').toString().toLowerCase();
    const bVal = (b[sortKey] || '').toString().toLowerCase();
    return aVal.localeCompare(bVal);
  });

  const totalPages = Math.ceil(filtered.length / itemsPerPage);
  const startIdx = (currentPage - 1) * itemsPerPage;
  const visibleItems = filtered.slice(startIdx, startIdx + itemsPerPage);

  const handleClear = () => {
    setQuery('');
    setCountryFilter('');
    setHideReagents(false);
    setHasSearched(false);
    setCurrentPage(1);
  };

  const t = {
    en: {
      title: "Chemical Search",
      placeholder: "Search by chemical name or CAS number",
      noResult: "No results found.",
      reset: "Reset",
      country: "Country",
      hideReagent: "Hide Reagent Vendors",
      allCountries: "All Countries",
      table: ["Chemical Name", "CAS No", "Manufacturer", "Country", "Website"]
    },
    ko: {
      title: "화학물질 검색",
      placeholder: "화학물질명 또는 CAS 번호로 검색",
      noResult: "검색 결과가 없습니다.",
      reset: "검색 초기화",
      country: "국가",
      hideReagent: "시약 판매업체 제외",
      allCountries: "전체 국가",
      table: ["화학물질명", "CAS 번호", "제조사", "국가", "웹사이트"]
    }
  }[lang];

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">{t.title}</h1>
        <select value={lang} onChange={e => setLang(e.target.value)} className="border p-1 rounded">
          <option value="en">English</option>
          <option value="ko">한국어</option>
        </select>
      </div>
      <input
        type="text"
        className="w-full p-2 border rounded mb-4"
        placeholder={t.placeholder}
        value={query}
        onChange={e => {
          setQuery(e.target.value);
          setHasSearched(true);
          setCurrentPage(1);
        }}
      />

      {hasSearched && (
        <>
          <div className="flex gap-4 items-center mb-4">
            <select
              className="p-2 border rounded"
              value={countryFilter}
              onChange={e => {
                setCountryFilter(e.target.value);
                setCurrentPage(1);
              }}
            >
              <option value="">{t.allCountries}</option>
              <option value="USA">USA</option>
              <option value="China">China</option>
              <option value="India">India</option>
              <option value="Germany">Germany</option>
            </select>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={hideReagents}
                onChange={() => {
                  setHideReagents(!hideReagents);
                  setCurrentPage(1);
                }}
              />
              {t.hideReagent}
            </label>
            <button
              onClick={handleClear}
              className="ml-auto bg-gray-200 px-3 py-1 rounded hover:bg-gray-300"
            >
              {t.reset}
            </button>
          </div>

          {filtered.length === 0 ? (
            <p className="text-gray-500">{t.noResult}</p>
          ) : (
            <>
              <table className="w-full border-collapse">
                <thead>
                  <tr className="bg-gray-100">
                    {['chemicalName', 'casNo', 'manufacturer', 'country', 'website'].map((key, i) => (
                      <th
                        key={key}
                        onClick={() => setSortKey(key)}
                        className="border p-2 text-left cursor-pointer hover:bg-gray-200"
                      >
                        {t.table[i]}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {visibleItems.map((chem, idx) => (
                    <tr key={idx} className="border-t">
                      <td className="p-2">{chem.chemicalName || '정보 없음'}</td>
                      <td className="p-2">{chem.casNo || '정보 없음'}</td>
                      <td className="p-2">
                        {Array.isArray(chem.manufacturer)
                          ? chem.manufacturer.join(', ')
                          : chem.manufacturer || '정보 없음'}
                      </td>
                      <td className="p-2">
                        {Array.isArray(chem.country)
                          ? chem.country.join(', ')
                          : chem.country || '정보 없음'}
                      </td>
                      <td className="p-2">
                        {Array.isArray(chem.website) && chem.website[0] ? (
                          <a href={chem.website[0]} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">
                            링크
                          </a>
                        ) : '정보 없음'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="flex justify-center gap-2 mt-4">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`px-3 py-1 rounded ${
                      page === currentPage ? 'bg-blue-500 text-white' : 'bg-gray-200 hover:bg-gray-300'
                    }`}
                  >
                    {page}
                  </button>
                ))}
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}