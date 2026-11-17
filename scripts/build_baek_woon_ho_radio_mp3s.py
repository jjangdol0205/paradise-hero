#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Synthesizes 5 genuine, ad-free Korean senior radio broadcast MP3 episodes
featuring DJ 김쌤 and Virtual Trot Singer 백운호 (白雲湖) for paradise-hero.com.
Zero real celebrity names; warm acoustic chord backing + -0.5 dBFS limiter.
"""

import asyncio
import json
import os
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

import edge_tts
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "assets" / "audio"
OUT_DIR.mkdir(parents=True, exist_ok=True)

VOICE_DJ = "ko-KR-SunHiNeural"
VOICE_BAEK = "ko-KR-InJoonNeural"

EPISODES = [
    {
        "id": "ep01",
        "filename": "baek_woon_ho_ep01.mp3",
        "segments": [
            (
                VOICE_DJ,
                "-4%",
                "+0Hz",
                "안녕하세요, 가족을 위해 평생을 바치신 어머님 아버님들의 따뜻한 쉼터, 김쌤의 영웅 라디오 일화 본방송입니다. 오늘 첫 사연은 대구 달서구에서 이순자 어머님이 보내주신 이야기입니다.",
            ),
            (
                VOICE_DJ,
                "-6%",
                "+0Hz",
                "작년 가을 남편을 먼저 떠나보내고 홀로 맞이하는 새벽 부엌이 참 시리고 쓸쓸했는데, 딸아이가 틀어준 백운호 가수님의 어머니의 봄날을 듣고 다시 살아갈 힘을 얻으셨다고 적어주셨네요.",
            ),
            (
                VOICE_BAEK,
                "-8%",
                "-6Hz",
                "이순자 어머님, 안녕하세요. 김쌤의 영웅 라디오 전속 가상 트로트 가수 백운호입니다. 거친 세월 앞치마에 눈물을 닦으시며 자식들 키워내신 어머님의 오늘이, 인생에서 가장 눈부신 봄날입니다.",
            ),
            (
                VOICE_BAEK,
                "-10%",
                "-6Hz",
                "찬 서리 내리던 새벽 부엌에, 따뜻한 보리차 끓이던 그 손길. 이제는 무거운 짐 내려놓으시고 꽃길만 걸으세요, 어머니의 봄날이 지금 피어납니다. 오늘도 식사 꼭 따뜻하게 챙겨 드시고 건강하십시오.",
            ),
        ],
    },
    {
        "id": "ep02",
        "filename": "baek_woon_ho_ep02.mp3",
        "segments": [
            (
                VOICE_DJ,
                "-4%",
                "+0Hz",
                "반갑습니다, 김쌤의 영웅 라디오 이화 저녁 사연 방송입니다. 오늘은 대전 유성구 오정숙 어머님께서 무릎 재활 산책길에 백운호 연가를 들으시며 보내주신 반가운 사연입니다.",
            ),
            (
                VOICE_DJ,
                "-6%",
                "+0Hz",
                "동네 공원을 천천히 세 바퀴 도실 때마다 잔잔한 중저음 가락이 발걸음을 가볍게 해주어 삼십 분 운동이 조금도 힘들지 않으시다고 전해 주셨습니다.",
            ),
            (
                VOICE_BAEK,
                "-8%",
                "-6Hz",
                "오정숙 어머님, 매일 저녁 포기하지 않고 걸으시는 그 걸음마다 건강한 기운이 가득 차오르길 백운호가 진심으로 응원합니다. 흰 구름 쉬어 가는 고요한 호수처럼 어머님의 저녁을 편안히 감싸드리겠습니다.",
            ),
            (
                VOICE_BAEK,
                "-10%",
                "-6Hz",
                "흰 구름 머무는 백운호 물결 위에, 지나온 세월을 가만히 띄워 보내고, 거친 파도 건너온 당신의 저녁에 따뜻한 항구의 등불을 밝혀 드립니다. 어머님, 환절기 바람에 무릎 따뜻하게 챙기세요.",
            ),
        ],
    },
    {
        "id": "ep03",
        "filename": "baek_woon_ho_ep03.mp3",
        "segments": [
            (
                VOICE_DJ,
                "-4%",
                "+0Hz",
                "어머님 아버님 편안하신가요, 김쌤의 영웅 라디오 삼화 감동 사연 시간입니다. 오늘은 전북 익산의 박정옥 어머님께서 칠순 고개에 보내주신 가슴 뭉클한 편지를 소개합니다.",
            ),
            (
                VOICE_DJ,
                "-6%",
                "+0Hz",
                "평생 삼 남매 뒷바라지하느라 내 이름 석 자도 잊고 살았는데, 다시 피는 동백꽃 가사를 들으며 남은 세월은 나를 위해 활짝 웃으며 살겠다고 다짐하셨답니다.",
            ),
            (
                VOICE_BAEK,
                "-8%",
                "-6Hz",
                "박정옥 어머님, 칠순이라는 귀한 세월의 고개를 넘으신 어머님께 깊은 존경의 박수를 올립니다. 겨울 찬 바람을 이겨내고 가장 붉게 피어나는 동백꽃은 바로 어머님의 인생을 닮았습니다.",
            ),
            (
                VOICE_BAEK,
                "-10%",
                "-6Hz",
                "눈보라 모질게 스쳐 간 가지 끝에, 누구보다 붉고 고운 꽃망울을 터뜨리네. 내 이름 석 자 다시 부르며 활짝 웃어보는 날, 다시 피는 동백꽃이 당신 가슴에 피어납니다.",
            ),
        ],
    },
    {
        "id": "ep04",
        "filename": "baek_woon_ho_ep04.mp3",
        "segments": [
            (
                VOICE_DJ,
                "-4%",
                "+0Hz",
                "정겨운 추억이 흐르는 김쌤의 영웅 라디오 사화 방송입니다. 강원도 강릉의 최선자 어머님께서 새벽녘 차 한 잔을 마시며 고향역 첫차를 듣고 보내주신 그리움의 편지입니다.",
            ),
            (
                VOICE_DJ,
                "-6%",
                "+0Hz",
                "젊은 시절 시골 정거장에서 도시로 떠나는 딸의 손에 따뜻한 보리차 병과 삶은 달걀을 쥐여주시던 친정어머니 얼굴이 떠올라 한참 눈시울을 적셨다고 하셨습니다.",
            ),
            (
                VOICE_BAEK,
                "-8%",
                "-6Hz",
                "최선자 어머님, 그 시절 친정어머님이 쥐여주시던 보리차 병의 온기가 오늘 어머님의 다정한 마음으로 고스란히 이어져 있습니다. 그리운 고향 정거장의 새벽 안개를 떠올리며 불러드립니다.",
            ),
            (
                VOICE_BAEK,
                "-10%",
                "-6Hz",
                "희미한 가로등 불빛 아래 고향역 첫차 기적 소리 울리면, 손 흔드시던 우리 어머니 주름진 두 손이 못내 그리워, 오늘도 마음은 고향역으로 달려갑니다.",
            ),
        ],
    },
    {
        "id": "ep05",
        "filename": "baek_woon_ho_ep05.mp3",
        "segments": [
            (
                VOICE_DJ,
                "-4%",
                "+0Hz",
                "깊어가는 시간, 김쌤의 영웅 라디오 오화 명곡 해설 방송입니다. 경기 수원 한상철 아버님과 서울 양천구 정명숙 님께서 부부 산책길에 내 인생의 금빛 노을을 즐겨 들으신다고 사연 주셨습니다.",
            ),
            (
                VOICE_BAEK,
                "-8%",
                "-6Hz",
                "한상철 아버님, 정명숙 어머님, 두 분이 나란히 걸으시는 저녁 산책길에 제 노래가 작은 동행이 되어 참 기쁩니다. 한낮의 뜨거운 태양보다 저녁 하늘을 물들이는 노을이 훨씬 더 깊고 아름답습니다.",
            ),
            (
                VOICE_BAEK,
                "-10%",
                "-6Hz",
                "어머니의 봄날부터 백운호 연가, 항구의 등불, 다시 피는 동백꽃, 고향역 첫차, 그리고 내 인생의 금빛 노을까지. 오직 어머님 아버님들의 평안한 황혼을 위해 백운호가 늘 곁에서 노래하겠습니다.",
            ),
            (
                VOICE_DJ,
                "-4%",
                "+0Hz",
                "매주 화요일과 금요일 저녁 여섯 시, 김쌤의 영웅 라디오 사랑방에서 따뜻한 사연과 함께 다시 찾아뵙겠습니다. 사랑방 가족 여러분, 오늘도 평안하고 건강하세요.",
            ),
        ],
    },
]


async def synth_segment(voice: str, rate: str, pitch: str, text: str, out_path: Path) -> None:
    comm = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
    await comm.save(str(out_path))


async def build_all() -> None:
    report = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for ep in EPISODES:
            seg_files = []
            for idx, (voice, rate, pitch, text) in enumerate(ep["segments"]):
                seg_mp3 = tmp_dir / f"{ep['id']}_s{idx}.mp3"
                await synth_segment(voice, rate, pitch, text, seg_mp3)
                seg_files.append(seg_mp3)

            # Create a 0.65s gentle pause file
            pause_wav = tmp_dir / f"{ep['id']}_pause.wav"
            subprocess.run(
                [
                    FFMPEG_EXE, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                    "-t", "0.65", str(pause_wav)
                ],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

            # Convert all segments to uniform 44.1kHz mono wav and concat
            concat_list = tmp_dir / f"{ep['id']}_concat.txt"
            lines = []
            for idx, sf in enumerate(seg_files):
                sw = tmp_dir / f"{ep['id']}_s{idx}.wav"
                subprocess.run(
                    [FFMPEG_EXE, "-y", "-i", str(sf), "-ar", "44100", "-ac", "1", str(sw)],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                lines.append(f"file '{sw.as_posix()}'")
                lines.append(f"file '{pause_wav.as_posix()}'")
            concat_list.write_text("\n".join(lines), encoding="utf-8")

            voice_wav = tmp_dir / f"{ep['id']}_voice.wav"
            subprocess.run(
                [
                    FFMPEG_EXE, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
                    "-c", "copy", str(voice_wav)
                ],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

            # Probe duration via stdlib wave
            with wave.open(str(voice_wav), "rb") as wf:
                dur = (wf.getnframes() / float(wf.getframerate())) + 1.8

            # Mix warm gentle F-major9 acoustic ambient chord pad (-24dB) under voice + -0.5 dBFS limiter
            out_mp3 = OUT_DIR / ep["filename"]
            pad_expr = (
                "aevalsrc=0.026*sin(2*PI*174.61*t)+0.020*sin(2*PI*220.00*t)+"
                "0.018*sin(2*PI*261.63*t)+0.012*sin(2*PI*329.63*t):s=44100:d=" + f"{dur:.2f}"
            )
            subprocess.run(
                [
                    FFMPEG_EXE, "-y",
                    "-i", str(voice_wav),
                    "-f", "lavfi", "-i", pad_expr,
                    "-filter_complex",
                    f"[1:a]afade=t=in:st=0:d=1.2,afade=t=out:st={max(0.5, dur-1.8):.2f}:d=1.6[bg];"
                    f"[0:a]adelay=500|500[vc];"
                    f"[vc][bg]amix=inputs=2:duration=longest:dropout_transition=2,"
                    f"alimiter=limit=0.94[outa]",
                    "-map", "[outa]",
                    "-ar", "44100", "-ac", "1", "-b:a", "64k",
                    str(out_mp3),
                ],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            report.append({
                "id": ep["id"],
                "file": str(out_mp3.relative_to(ROOT)),
                "bytes": out_mp3.stat().st_size,
                "duration_sec": round(dur, 1),
            })

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(build_all())
