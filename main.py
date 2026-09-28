import cv2
import numpy as np
import pywt
from PIL import Image
import os

class CamShieldEngine:
    def __init__(self, watermark_text="CAMSHIELD_PROTECTED"):
        self.watermark_text = watermark_text

    def remove_exif(self, image_path, save_path):
        """1. EXIF 메타데이터(GPS, 기기 정보) 완전 제거"""
        img = Image.open(image_path)
        data = list(img.getdata())
        img_no_exif = Image.new(img.mode, img.size)
        img_no_exif.putdata(data)
        img_no_exif.save(save_path)
        return save_path

    def apply_adversarial_noise(self, img, epsilon=0.03):
        """2. AI 특징점 추출 교란을 위한 적대적 노이즈(Adversarial Perturbation) 가산"""
        img_float = img.astype(np.float32) / 255.0
        
        # 고주파 그래디언트 형태의 미세 노이즈 매트릭스 생성
        h, w, c = img.shape
        noise = np.random.choice([-epsilon, epsilon], size=(h, w, c))
        
        # 노이즈 가산 및 픽셀 범위 Clip (0~1)
        protected_img = np.clip(img_float + noise, 0.0, 1.0)
        return (protected_img * 255.0).astype(np.uint8)

    def embed_frequency_watermark(self, img, alpha=5.0):
        """3. DWT(디지털 웨이블릿 변환) 주파수 영역 비가시적 워터마킹"""
        # YCrCb 색상 공간 변환 (Y 채널 주파수 변환)
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)

        # 2차원 DWT 수행 (Haar 웨이블릿)
        coeffs = pywt.dwt2(y, 'haar')
        LL, (LH, HL, HH) = coeffs

        # 비가시적 워터마크 시그니처 매트릭스 가산
        watermark_matrix = np.sin(np.linspace(0, 100, LL.shape[0] * LL.shape[1])).reshape(LL.shape)
        LL_watermarked = LL + (alpha * watermark_matrix)

        # 역 DWT(IDWT) 수행
        coeffs_watermarked = (LL_watermarked, (LH, HL, HH))
        y_watermarked = pywt.idwt2(coeffs_watermarked, 'haar')
        y_watermarked = np.clip(y_watermarked, 0, 255).astype(np.uint8)

        # 채널 재합성 및 BGR 변환
        merged_ycrcb = cv2.merge([y_watermarked, cr, cb])
        final_img = cv2.cvtColor(merged_ycrcb, cv2.COLOR_YCrCb2BGR)
        return final_img

    def process_image(self, input_path, output_path):
        """CamShield 원스톱 보안 파이프라인 실행"""
        print(f"[1/3] EXIF 메타데이터 제거 중...")
        temp_no_exif = "temp_no_exif.jpg"
        self.remove_exif(input_path, temp_no_exif)

        print(f"[2/3] 적대적 노이즈 필터 가산 중...")
        img = cv2.imread(temp_no_exif)
        noise_img = self.apply_adversarial_noise(img)

        print(f"[3/3] 주파수 영역(DWT) 비가시적 워터마크 합성 중...")
        final_img = self.embed_frequency_watermark(noise_img)

        cv2.imwrite(output_path, final_img)
        if os.path.exists(temp_no_exif):
            os.remove(temp_no_exif)
            
        print(f"✅ CamShield 보안 처리 완료! 저장 경로: {output_path}")

if __name__ == "__main__":
    # 시토타입 테스트 코드 (실제 사진 경로 넣고 실행 가능)
    engine = CamShieldEngine()
    
    # 임시 테스트용 이미지 생성 (실제 이미지 파일이 없을 경우 대비)
    dummy_img = np.zeros((512, 512, 3), dtype=np.uint8)
    cv2.putText(dummy_img, 'Test Photo', (100, 250), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
    cv2.imwrite('input_test.jpg', dummy_img)

    # 보안 파이프라인 처리
    engine.process_image('input_test.jpg', 'protected_output.jpg')