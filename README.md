# CamCamShield Prototype 캠캠쉴드 프로토타입

> **On-Device AI 기반 딥페이크 성범죄 예방 및 이미지 도용 방지 보안 카메라 앱 시제품 로직**

본 레포지토리는 SNS 업로드 전 단계에서 원본 사진의 개인정보와 초상권을 원스톱으로 보호하는 캠캠쉴드의 파이프라인 소스코드입니다.

---

## 주요 기술

1. **EXIF Metadata Stripping**
   - 사진 내 포함된 GPS 위치 정보, 촬영 기기 정보 등 개인 신상 단서 메타데이터 자동 삭제.
2. **적대적 노이즈**
   - 생성 AI(Diffusion, GAN 등) 인코더의 특징점 추출을 방해하는 미세 고주파 노이즈 실시간 가산.
3. **DWT Frequency Domain Invisible Watermarking**
   - 이미지 주파수 영역(DWT) 깊은 곳에 추적용 비가시적 워터마크를 삽입하여, SNS 자동 압축(JPEG Resize) 이후에도 원본 증명 및 유포 경로 추적 가능.

---

## 실행 환경 및 필수 라이브러리

- Python 3.9+
- Dependencies:
  ```bash
  pip install opencv-python numpy PyWavelets Pillow
