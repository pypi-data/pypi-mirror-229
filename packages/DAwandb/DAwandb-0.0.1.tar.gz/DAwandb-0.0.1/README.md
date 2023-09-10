# README.md

# Yonsei Univ. DA 5기 실습을 위한 WandB

# Wandb란?

<aside>
✏️ wandb는 MLOps 플랫폼으로 머신러닝, 딥러닝을 학습하는데 필요한 다양한 기능들을 제공한다. 대표적으로 아래의 기능등을 갖추고 있다.

</aside>

- 실험관리
- 하이퍼파라미터 튜닝
- 데이터, 모델 버저닝
- 모델 관리
- 데이터 시각화
- 협업 리포트

![https://blog.kakaocdn.net/dn/eBD6VD/btrNvhHyJn9/mNh6tMXM0giLGXJfCI3dZK/img.png](https://blog.kakaocdn.net/dn/eBD6VD/btrNvhHyJn9/mNh6tMXM0giLGXJfCI3dZK/img.png)

# 실습 전 wandb 환경 구축

## 1. wandb 회원가입 및 API Key 확인

[링크](https://wandb.auth0.com/login?state=hKFo2SBjMXRvVnpWOE5HNG5fUVp3Rm9PV0ZTV3o0R1FwclNTYqFupWxvZ2luo3RpZNkgWEhmdDQyOU9LajNYZXZ2U2hPZFlaYUItczNwMzhKZHajY2lk2SBWU001N1VDd1Q5d2JHU3hLdEVER1FISUtBQkhwcHpJdw&client=VSM57UCwT9wbGSxKtEDGQHIKABHppzIw&protocol=oauth2&nonce=Y1p5c2FJeEhBRkhqby5Gag%3D%3D&redirect_uri=https%3A%2F%2Fapi.wandb.ai%2Foidc%2Fcallback&response_mode=form_post&response_type=id_token&scope=openid%20profile%20email&signup=true)

## 2. anaconda 설치 후 가상환경 구축

```bash
> conda create -n wandb(name)
```

- 아나콘다 없을 시 참고
    
    [https://benn.tistory.com/26](https://benn.tistory.com/26)
    

## 3. 설치(기본)

```bash
MacOS
> pip3 install wandb

Wi
> pip install wandb
```

- pip가 없는 경우 참고
    
    환경변수 설정에 따라 달라질 수 있음 But 일반적으로
    
    - MacOS
        
        ```bash
        > python3 get-pip.py
        > pip3 install --upgrade pip3
        ```
        
    - Wi
        
        ```bash
        	# Wi(powershell)
        > python get-pip.py
        > pip install --upgrade pip
        ```
        

## 3. 설치(간단)

```bash
pip3 install DAwandb
pip3 install -r requirements.txt
```
## 예시파일 실행
```bash
python3 main2.py --project_name DA_wandb --task_name  1 --model 1
```