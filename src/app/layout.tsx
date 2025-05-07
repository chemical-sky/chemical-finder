export const metadata = {
  title: 'ChemFinder',
  description: '전세계 화학물질 검색 포털',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <head>
        {/* Google Analytics */}
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-7FC53GBLH7"></script>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', 'G-7FC53GBLH7');
            `,
          }}
        ></script>
      </head>
      <body>{children}</body>
    </html>
  );
}
