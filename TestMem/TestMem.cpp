#include <iostream>
#include <windows.h>

using namespace std;

int main(int argc, char* argv[]) {
    HANDLE hFile = CreateFileA(argv[1], GENERIC_READ, NULL, NULL, OPEN_EXISTING, 0, NULL);
    DWORD fileSize = GetFileSize(hFile, NULL);
    PVOID pCode = VirtualAlloc(NULL, fileSize, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    DWORD readFileSize;
    ReadFile(hFile, pCode, fileSize, &readFileSize, NULL);
    HANDLE hThread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)pCode, Sleep, 0, NULL);
    WaitForSingleObject(hThread, INFINITE);
}