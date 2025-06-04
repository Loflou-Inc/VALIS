@echo off
cd /d C:\VALIS\local_llm\llama.cpp
.\build\bin\Release\llama-server.exe ^
--model C:\VALIS\local_llm\models\mistral-7b-instruct-v0.1.Q4_K_M.gguf ^
--port 8080 ^
--ctx-size 4096 ^
--threads 8 ^
--mlock