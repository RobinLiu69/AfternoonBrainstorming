# 午後激盪 規則介紹

[![Static Badge](https://img.shields.io/badge/lang-en-red)](https://github.com/RobinLiu69/AfternoonBrainstorming/blob/main/README.en.md)
[![Static Badge](https://img.shields.io/badge/lang-zh.tw-blue)](https://github.com/RobinLiu69/AfternoonBrainstorming/blob/main/README.md)

## 遊戲簡介
你將會有12張卡牌(在遊戲開始前組建它)，而每一回合你會獲得一次攻擊機會(可以存下來)，你可以透過召喚手下或使用魔法的方式去取得優勢。

每一個場上未被麻痺的手下使你獲得一分，雙方的分數會互相抵消，最先領先對手10分的玩家即獲得勝利。
## 遊戲開始前
![Screenshot_20241007_214036](https://github.com/user-attachments/assets/2c5819b8-a59d-4ed5-9383-99700cbd5b8c)

組建你的12張牌，每種手下最多攜帶兩張，法術最多攜帶三張。
優先玩家選取好6張牌後交由下一位玩家選取(透過**E**鍵兩段式切換)12張牌，再輪回第一位玩家選取，再選取階段你只能看到對手的前六張牌。

> [!TIP]
> - **S**與滑鼠位置來選牌。
>
> - **A**、**D**上一頁及下一頁;**空白鍵**也可以用來下一頁。
>
> - **C**來清除最後選擇的牌。
>
> - **E**來切換玩家(按一次後會將雙方牌組隱藏，只顯示前6張，再按一次後會顯示下一位的牌組)。
>
> - **T**來開啟與關閉計時器。
>
> - **Y**來決定結算之圖表是否保存。
>
> - **R**遊戲開始(需按兩次)。

## 遊戲開始時
![Screenshot_20241007_214217](https://github.com/user-attachments/assets/c43a401e-7ef3-4e99-9be7-cc68e746a586)

先手玩家(左方玩家)擁有三張手牌，和一次攻擊機會。

後手玩家則會在他的回合開始時擁有四張手牌和一次攻擊機會。

> [!IMPORTANT]
> 雙方皆能看到對方手牌。
> 每回合從抽牌堆抽一張牌並獲得一次攻擊機會。

> [!NOTE]
> 攻擊次數顯示於下方兩側的方塊數,依序為白, 青, 紅, 每個顏色有10次

> [!TIP]
> - **1-9**、**0** 依序將對應位置的手牌放置到滑鼠位置的格子(或施放法術)。
>
> - **空白鍵**用於放置手牌中最後一張
> 
> - **A**可以進行攻擊
>
> - **E**結束你的回合
>
> - 下方會顯示牌庫和棄牌堆，手下死亡或法術牌被使用會進入棄牌堆

# 魔法牌
![Screenshot_20241007_215820](https://github.com/user-attachments/assets/55934318-f37a-413f-87b4-16635bc5582f)

- **方塊(CUBES)**
  - 使用後在場上選擇兩個點(鍵盤 **P**)放置小方塊(**CUBE**)，血量為4點無攻擊力為中立單位。

- **回血(HEAL)**
  - 使用滑鼠與(鍵盤 **H**)為單位回復5點血量，血量有最大值。

> [!NOTE]
> 所有回復效果的回血若溢出自身最大血量則以每兩點轉換成一點護盾

- **移動(MOVE)**
  - 使用此牌後先選擇一個友方單位(鍵盤 **M**)，接著該友方單位背賦予移動中效果(**Moving**)會顯示在攻擊力下方。

> [!NOTE]
> 對移動中的牌使用(鍵盤 **M**)則會使其進入選取中狀態(**Selected**)，再選周圍九宮格且為空的地方再次按下(鍵盤 **M**)，該單位便會移動到那。

> [!WARNING]
> 暈眩狀態下的單位無法使用移動。

# 效果簡介
- **暈眩(numbness)**
  - 無法攻擊移動與得分，但自身效果依舊會被觸發。

> [!IMPORTANT]
> 單位剛放置時會被賦予此效果，所有派系的刺客除外。

- **護甲(armor)**
  - 沒有最大值，且當被攻擊時，會先攻擊到護甲，直到歸零後，血量才會被攻擊到。

> [!WARNING]
> 破甲效果會使護甲直接歸零。

- **移動中(moving)**
  - 當玩家使用了移動牌在友方單位，該單位會顯示移動中。

> [!IMPORTANT]
> 如果是移動中和暈眩同時存在依舊可以移動。

> [!NOTE]
> 若場上有不只一隻擁有移動中效果之單位，則可用滑鼠位置與M鍵，選定要移動的移動中單位，並賦予選取(Selected)效果。

- **選取效果(Selected)**
  - 用於決定哪隻移動中單位要移動。

- **狂報狀態(anger/rage)**
  - 該效果因應單位效果而定。

- **幸運效果**
   - **好運效果**
     以下五種好運效果出現機率各為20%
       - 護甲+4
       - 自身攻擊乘2
       - 攻擊一次(依該單位攻擊而異)
       - 附加移動中效果
       - 在該幸運方塊上下左右放置一格幸運方塊(假若是綠色法師效果則此項為無效果)
   - **壞運效果**
     以下五種好運效果出現機率各為20%
       - 破盾
       - 獲得暈眩效果
       - 血量除2
       - 攻擊除2
       - 要是血量高於等於2則血量減2，否則無(不會觸發單位被攻擊或擊殺效果)

# 攻擊方式

- **大十字：** 攻擊處於同一列和同一排的單位

- **小十字：** 攻擊上下左右的單位

- **九宮格：** 攻擊周圍的單位

- **斜十字：** 攻擊左上，左下，右上，右下的單位

- **單體最近：** 攻擊最近的單位

- **單體最遠：** 攻擊最遠的單位

# 派系介紹

![Screenshot_20241007_215700](https://github.com/user-attachments/assets/192971d8-e20d-4e2c-8b89-e6352705c007)

## 白色派系

- **三角形(ADC)-5/4-大十字**
- **圓形(AP)-4/3-單體最近**/攻擊附帶麻痺。
- **方形(TANK)-15/1-小十字**
- **梯形(HF)-9/2-九宮格**
- **雙菱形(LF)-7/4-小十字**
- **刺客(ASS)-2/5-斜十字**
- **六邊形(APT)8/2-單體最近**/攻擊為自己及最近友方附加自身攻擊點護盾。
- **鑽石(SP)-1/5-單體最遠**/每回合額外多得一分。

## 紅色派系

- **三角形(ADC)-4/2-大十字**/造成傷害後+1攻擊力。
- **圓形(AP)-3/2-單體最近**/攻擊附帶麻痺，並偷取敵方100%攻擊力。
- **方形(TANK)-8/1-小十字**/承受傷害後為最近隊友附加2點護盾。
- **梯形(HF)-9/1-九宮格**/每次造成傷害則減少1點血且獲得1點攻擊，且此傷害不會直接使紅重裝死亡，而是延遲至回合結束。
> [!IMPORTANT]
> 其不會獲得分數。
- **雙菱形(LF)-6/2-小十字**/造成傷害後+1/+1。
- **刺客(ASS)-2/4-斜十字**/斬殺敵人後，為最近隊友攻擊力+2。
- **六邊形(APT)-6/2-單體最近**/攻擊給自己及最近隊友+1/+1。
- **鑽石(SP)-1/5-單體最遠**/所有紅色系所獲得的增益都會疊加在他身上。

## 綠色派系

- **三角形(ADC)-3/3-大十字**/攻擊後，會在攻擊範圍內50%生成幸運寶箱。
- **圓形(AP)-3/2-單體最近**/攻擊附帶麻痺和隨機壞運效果，並獲得隨機好運效果或無。 (詳見[效果介紹](#效果簡介))
- **方形(TANK)-9/1-小十字**/承受傷害後依敵方幸運效果附加壞運效果或無。(詳見[效果介紹](#效果簡介))
- **梯形(HF)-8/1-九宮格**/破壞方塊會增加5%運氣值，並隨機位置放一個幸運方塊。
- **雙菱形(LF)-6/3-小十字**/破壞幸運方塊便對最近敵方單位造成4點傷害，且有25%返還刀。
- **刺客(ASS)-2/4-斜十字**/斬殺後獲得5%運氣值，且敵方運氣值減少5%。
- **六邊形(APT)-6/0-單體最近**/回合開始時，會將小十字內的空格放上幸運方塊，已方每放置幸運方塊獲得1點護盾。
- **鑽石(SP)-?/?-單體最遠**/運氣值增加10%，隨機位置放置(每多出10幸運值)個幸運方塊。 ~~(血量絕對不是1，攻擊絕對不是5)~~

> [!NOTE]
> **綠色特殊單位**
>
> **幸運方塊(luckyblock)-1/0**-類似方塊但被迫壞掉後會給予破壞單位隨機效果，依該單位所屬者之運氣值而定。 (詳見[效果介紹](#效果簡介))

## 藍色派系

- **三角形(ADC)-4/2-大十字**/利用藍球抽牌後會自動攻擊，若當下為麻痹效果則解除麻痹但不攻擊，展殺後獲得2點藍球。
- **圓形(AP)-4/2-單體最近**/攻擊附帶麻痺並獲得兩顆藍球。
- **方形(TANK)-10/1-小十字**/承受傷害後會獲得一顆藍球。
- **梯形(HF)-8/2-九宮格**/攻擊以現有藍球造成額外傷害。
- **雙菱形(LF)-7/3-小十字**/造成傷害會獲得一顆藍球。
- **刺客(ASS)-2/4-斜十字**/斬殺後獲得兩顆藍球。
- **六邊形(APT)-5/3-單體最近**/獲得藍球時會獲得1護盾，攻擊時每3點護盾獲得1顆藍球。
- **鑽石(SP)-1/5-單體最遠**/放置時對隨機敵人造成一點傷害，重複(我方棄牌堆+我方場上堆)次。

> [!NOTE]
> **藍球(token):** 此數值只應用於藍色牌組，當此數值達到3時，該玩家將從牌堆抽一次牌。

## 橘色派系

- **三角形(ADC)-4/2-大十字**/攻擊後可移動，移動後會自動攻擊。
- **圓形(AP)-3/2-單體最近**/攻擊附帶麻痺，回合開始會獲得一個本回合可使用的移動魔法牌。
- **方形(TANK)-10/1-小十字**/承受傷害後會獲得一個本回合可使用的移動魔法牌。
- **梯形(HF)-9/1-九宮格**/攻擊後可移動並獲得+1攻擊力，回合結束會消失。
- **雙菱形(LF)-6/3-小十字**/攻擊後可移動並對單體最近再次造成傷害。
- **刺客(ASS)-2/3-斜十字**/斬殺後可移動，移動會進入狂暴 (詳見[效果介紹](#效果簡介))，狂暴狀態下斬殺會返回刀並解除狀態。
- **六邊形(APT)-6/0-單體最近**/隊友移動後為自己及移動友方附加一點護盾，自身移動則護盾以2比1轉為攻擊力。
- **鑽石(SP)-1/5-單體最遠**/隊友移動後對單體最遠造成3點傷害。

> ~~(今天 19:52 你吃完了嗎)(今天 21:22 吃完了啦...)~~

## 墨綠派系(圖騰派系)

- **三角形(ADC)-4/2-長十字**/攻擊時額外造成圖騰的1/4的傷害。
- **圓形(AP)-3/3-單體最近**/攻擊刻印5層。
- **方形(TANK)-9/1-小十字**/受到傷害刻印2層。
- **梯形(HF)-8/2-九宮格**/我方回合開始後受到2傷害並刻印2，造成傷害後恢復1點血。
- **雙菱形(LF)-6/3-小十字**/置時對攻擊範圍內敵人造成圖騰的1/4傷害，攻擊依範圍內每單位獲得1刻印。
- **刺客(ASS)-2/4-斜十字**/斬殺後死亡，展殺每隻刻印7。
- **六邊形(APT)-6/0-單體最近**/攻擊時依序觸發:額外造成圖騰的1/2的傷害，獲得護盾量1/2的刻印層數，獲得造成傷害的1/2的護盾。
- **鑽石(SP)-1/5-單體最遠**/在場時，刻印數量翻倍。

## 淺藍派系(海盜派系)

- **三角形(ADC)-4/1(6)-長十字**造成傷害後打劫2$/雙重打擊(+1/+2)。
- **圓形(AP)-4/1(4)-單體最近**/放置時為最近敵方附上印記，所有最近單體及最遠單體攻擊時，皆會同時對其造成傷害/對印記敵方造成傷害打劫3$(+1/+2)。
- **方形(TANK)-9/1(4)-小十字**/被攻擊時獲得2$/第一次攻擊，不會受到傷害(也不會觸發敵方特性)(+2/+0)。
- **梯形(HF)-7/1(6)-九宮格**/造成傷害後打劫2$/死亡後，會多留存一回合並+2攻擊力(+2/+1)。
- **雙菱形(LF)-5/2(4)-小十字**/造成傷害後打劫2$/回合開始時獲得隨機攻擊模式(+2/+2)。
- **刺客(ASS)-1/3(4)-斜十字**/斬殺後打劫5$/第一次攻擊+2攻擊(+1/+1)。
- **六邊形(APT)-2/1(6)-單體最近**/每5$使其受到傷害減1(最多三)/回合開始時+4$(+5/+1)。
- **鑽石(SP)-1/2(6)-單體最遠**/獲得10$/在場的時候，消耗的金幣減二(+1/+3)。

> [!NOTE]
> **錢幣(coin):** 此數值只應用於淺藍牌組，此數值可用來讓角色進化，上方血量攻擊後的括弧內的數字，為升級所需消耗的金幣。最多可擁有50金幣。
> 
> 角色介紹斜線後的能力，為進化後所擁有的額外能力，不管有無進化接會有前方的能力，而最後面的括弧，則為進化後所增加的血量和攻擊。

> [!IMPORTANT]
> 進化只可在手牌時進行。
> 將滑鼠移至要進化的牌，並點擊該位置的數字鍵，就進化完成，進化不需要消耗錢幣，只在放置時扣除。

## 桃紅派系(依影派系)

> [!NOTE]
> **影子(shadow):** 當此派係放置時(刺客除外)，將在已中心為對稱中心的對稱點，放置一個不可被攻擊、移動、回血的單位(也不會被效果指定)，若本體移動影子也會移動到相應位置，若本體死亡則影子自動消散，影子在場不會獲得分數。


> [!IMPORTANT]
> 若影子攻擊區內有人，但本體攻擊區內沒人，也可以正確攻擊。

- **三角形(ADC)-4/2-長十字**/本體攻擊則影子也會攻擊。
- **圓形(AP)-4/1-單體最近**/對格子內的敵人持續附加麻痺效果。
- **方形(TANK)-10/1-小十字**/影子位置不可放置單位。
- **梯形(HF)-8/1-九宮格**/本體攻擊則影子也會攻擊。
- **雙菱形(LF)-6/2-小十字**/攻擊到敵人時, 已影子為中心對單體最近敵人造成傷害，若本體與影子對同單位造成傷害，則再對其造成一次傷害。
- **刺客(ASS)-2/3-斜十字**/斬殺則在死亡的敵人位置，放置不移動的影子,本體攻擊影子也會攻擊。
- **六邊形(APT)-2/3-單體最近**/影子上友方減少50%受到的傷害，並將其轉移為護盾並附加在自己身上。
- **鑽石(SP)-1/5-單體最遠**/上場時生成最遠友方的影子的複製(該影子不可移動)。

## 紫色派系

- **圓形(AP)-3/1-單體最近**/上場時，對最近單位破盾並將攻擊力降為該單位原本的攻擊力。自身攻擊也有此效果，但多附帶麻痺。
- **方形(TANK)-9/1-小十字**/敵人移動後損失2點生命值。
> [!IMPORTANT]
> 不被麻痹效果所無效化
- **刺客(ASS)-2/3-斜十字**/斬殺後抽(敵方場上堆-我方場上堆-3)張牌。
- **梯形(HF)-8/1-九宮格**/當自己回合開始時計算所有在他攻擊範圍內的敵方單位(不包含中立單位)，並增加(該數值/3)的攻擊次數。

# 結尾結算畫面
## 分數玩家顯示
![Screenshot_20241007_214359](https://github.com/user-attachments/assets/a71dd9fe-2aa4-4d0f-92c8-9d00ca980e8f)
## 玩家圖表數據顯示
![Screenshot_20241007_214542](https://github.com/user-attachments/assets/844ffd88-eb28-4360-b78d-275cf2fd9287)
## 雙方玩家表格顯示
![Screenshot_20241007_214508](https://github.com/user-attachments/assets/4f354a9e-369b-43cb-b3e4-65a5501633d8)


> [!TIP]
> 用 **Tab** 來查看雙方玩家所有數據，上方為**Player1**的數據，下方為**Player2**的數據
> 使用數字鍵 **1**，**2**，**SPACE** 切換玩家圖表
> **ESC** 退出

## 數據解釋
**KDA:** 擊殺數/死亡數

**Average Attack Damage:** 造成傷害/攻擊次數 

**Per Round Influence:** 造成傷害\*受到傷害/存活回合數

**Survival Index:** ((得分數\*2)+(造成傷害/攻擊次數\*2)+(受到傷害/受到傷害次數\*2))/存活回合數

# 外部連結
[巴哈規則](https://home.gamer.com.tw/artwork.php?sn=5702820)
> [!CAUTION]
> 以這裡的規則為主!!!!

[Godot Version](https://github.com/AaronCheng1996/AfternoonBrainstorming_godot)
