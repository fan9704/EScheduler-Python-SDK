"""EScheduler SDK 團隊認證範例"""

import asyncio

from escheduler_sdk import ESchedulerSDK, AuthenticationError, ValidationError


async def team_auth_example():
    """團隊認證範例"""
    
    # 初始化 SDK
    async with ESchedulerSDK(
        base_url="http://localhost:8000",  # 替換為你的 EScheduler API URL
        timeout=30.0
    ) as sdk:
        
        try:
            # 方法 1: 使用 SDK 的便利方法進行認證
            print("=== 方法 1: 使用 SDK 便利方法認證 ===")
            auth_success = await sdk.authenticate("ABCD")  # 替換為你的團隊 token
            if auth_success:
                print("✅ 認證成功")
                print(f"   已認證狀態: {sdk.is_authenticated()}")
            else:
                print("❌ 認證失敗")
            
            # 方法 2: 直接使用團隊 API 進行認證
            print("\n=== 方法 2: 直接使用團隊 API 認證 ===")
            
            # 先登出清除之前的認證
            sdk.logout()
            print(f"   登出後認證狀態: {sdk.is_authenticated()}")
            
            # 進行認證並獲取詳細回應
            auth_response = await sdk.team.auth_and_set_token("ABCD")
            print(f"✅ 認證回應:")
            print(f"   認證狀態: {auth_response.status}")
            if auth_response.team:
                print(f"   團隊 ID: {auth_response.team.id}")
                print(f"   團隊名稱: {auth_response.team.name}")
            if auth_response.access_token:
                print(f"   JWT Token: {auth_response.access_token[:20]}...")
            
            # 方法 3: 獲取所有團隊
            print("\n=== 方法 3: 獲取所有團隊 ===")
            teams = await sdk.team.get_all_teams()
            print(f"✅ 共有 {len(teams)} 個團隊:")
            for team in teams:
                print(f"   - {team.name} (ID: {team.id})")
            
            # 方法 4: 透過 token 獲取團隊信息
            print("\n=== 方法 4: 透過 token 獲取團隊信息 ===")
            team = await sdk.team.get_team_by_token("ABCD")
            if team:
                print(f"✅ 團隊信息:")
                print(f"   ID: {team.id}")
                print(f"   名稱: {team.name}")
            else:
                print("❌ 無效的 token")
            
            # 方法 5: 手動認證流程
            print("\n=== 方法 5: 手動認證流程 ===")
            
            # 先清除認證
            sdk.logout()
            
            # 手動進行認證但不自動設置 token
            auth_response = await sdk.team.auth_team("ABCD")
            if auth_response.status and auth_response.access_token:
                # 手動設置 JWT token
                sdk.client.set_jwt_token(auth_response.access_token)
                print("✅ 手動認證並設置 token 成功")
                print(f"   認證狀態: {sdk.is_authenticated()}")
            
        except AuthenticationError as e:
            print(f"❌ 認證錯誤: {e}")
            print(f"   狀態碼: {e.status_code}")
            
        except ValidationError as e:
            print(f"❌ 驗證錯誤: {e}")
            print(f"   狀態碼: {e.status_code}")
            print("   請檢查 token 格式是否正確 (應為4位字符)")
            
        except Exception as e:
            print(f"❌ 未知錯誤: {e}")
            print(f"   錯誤類型: {type(e).__name__}")


async def test_invalid_tokens():
    """測試無效 token 的處理"""
    
    print("\n=== 測試無效 token 處理 ===")
    
    async with ESchedulerSDK(base_url="http://localhost:8000") as sdk:
        
        # 測試格式錯誤的 token
        invalid_tokens = [
            "ABC",      # 太短
            "ABCDE",    # 太長
            "12345",    # 超過4位
            "",         # 空字符串
            "ab cd",    # 包含空格
        ]
        
        for token in invalid_tokens:
            try:
                print(f"\n測試 token: '{token}'")
                auth_response = await sdk.team.auth_team(token)
                print(f"   意外成功: {auth_response.status}")
            except ValidationError as e:
                print(f"   ✅ 正確捕獲驗證錯誤: {e.message}")
            except Exception as e:
                print(f"   ❌ 其他錯誤: {e}")
        
        # 測試格式正確但無效的 token
        try:
            print(f"\n測試無效但格式正確的 token: 'ZZZZ'")
            auth_response = await sdk.team.auth_team("ZZZZ")
            if not auth_response.status:
                print(f"   ✅ 正確返回認證失敗: {auth_response.status}")
            else:
                print(f"   ❌ 意外認證成功")
        except AuthenticationError as e:
            print(f"   ✅ 正確捕獲認證錯誤: {e.message}")
        except Exception as e:
            print(f"   ❌ 其他錯誤: {e}")


if __name__ == "__main__":
    # 運行團隊認證範例
    asyncio.run(team_auth_example())
    
    # 運行無效 token 測試
    asyncio.run(test_invalid_tokens())