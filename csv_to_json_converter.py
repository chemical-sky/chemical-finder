import pandas as pd
import json

# ECHA에서 받은 전체 CSV 파일 로드
# CSV 파일명은 이미 다운된 파일명과 동일해야 함
csv_file = 'echa_registered_substances.csv'
df = pd.read_csv(csv_file)

# 실제 열 이름을 기준으로 필요한 열 추출
# 열 이름이 정확하지 않으면 print(df.columns)로 확인 후 수정
if 'Substance Name' in df.columns and 'CAS' in df.columns:
    df = df[['Substance Name', 'CAS']]
    df.columns = ['chemicalName', 'casNo']
else:
    print("❌ 필요한 열이 없습니다. 열 이름을 확인해주세요.")
    exit()

# 결측값 제거, 중복 제거
df = df.dropna().drop_duplicates()

# 상위 10,000개 항목만 추출
df = df.head(10000)

# 제조사 정보는 현재 없음 → 빈 필드 추가
df['manufacturer'] = ''
df['country'] = ''
df['website'] = ''

# JSON으로 저장
output_file = 'registered_chemicals.json'
df.to_json(output_file, orient='records', indent=2, force_ascii=False)
print(f"✅ JSON 파일 생성 완료! → {output_file}")
