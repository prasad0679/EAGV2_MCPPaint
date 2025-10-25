# --- Core Imports ---
from mcp.server.fastmcp import FastMCP, Image
from mcp.types import TextContent, EmbeddedResource, BlobResourceContents
from mcp import types
from PIL import Image as PILImage # Used for image manipulation if needed later (not used currently)
import math
import sys
import json
import os
import time
import asyncio
import pyautogui
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
# --- GUI Automation Imports ---
# NOTE: These libraries (pywinauto, win32gui, etc.) are blocking and must run in a separate thread.
from pywinauto.application import Application
from pywinauto import mouse, keyboard
import win32gui
import win32con
import win32api
from win32api import GetSystemMetrics

# --- CONFIGURATION ---
PAINT_TITLE = "Untitled - Paint"  # 👈 Re-verify this is EXACTLY correct

# --- Coordinates (You MUST verify these again!) ---
# Find these using the pyautogui.mouseInfo() tool.
# TEXT_TOOL_X = 512
# TEXT_TOOL_Y = 129
# RECTANGLE_TOOL_X = 802  # X-coordinate of the Rectangle button on your screen
# RECTANGLE_TOOL_Y = 136  # Y-coordinate of the Rectangle button on your screen
# CANVAS_START_X = 500    # Starting X coordinate on the screen
# CANVAS_START_Y = 500    # Starting Y coordinate on the screen
# RECTANGLE_WIDTH = 300   # How wide the rectangle should be
# RECTANGLE_HEIGHT = 200  # How tall the rectangle should be

TEXT_TOOL_X = 337
TEXT_TOOL_Y = 91
RECTANGLE_TOOL_X = 527  # X-coordinate of the Rectangle button on your screen
RECTANGLE_TOOL_Y = 85  # Y-coordinate of the Rectangle button on your screen
CANVAS_START_X = 500    # Starting X coordinate on the screen
CANVAS_START_Y = 500    # Starting Y coordinate on the screen
RECTANGLE_WIDTH = 300   # How wide the rectangle should be
RECTANGLE_HEIGHT = 200  # How tall the rectangle should be
# ----------------------------------------------------

# print("from paint_server.py, cwd:", os.getcwd())

# Create MCP server instance
mcp = FastMCP("MCP Server Paint App")

# ThreadPoolExecutor for running blocking GUI operations on a single worker thread.
# This serializes the GUI operations, which is crucial for stability.
executor = ThreadPoolExecutor(max_workers=1)

async def run_in_thread(func, *args, **kwargs):
    """Utility to run a blocking function in the dedicated thread pool."""
    loop = asyncio.get_running_loop()
    # Ensure the thread pool waits for the function execution to complete
    return await loop.run_in_executor(executor, lambda: func(*args, **kwargs))


def draw_red_rectangle(hwnd: int, x1: int, y1: int, x2: int, y2: int):
    """
    Blocking function that performs the actual drawing using pywinauto/win32gui.
    """
    hwnd = int(hwnd)
    
    # 1. Activate and Focus the Paint window
    try:
        # Connect to Paint window, ensuring we use the UIA backend for reliable ribbon access.
        paint_app = Application(backend="uia").connect(handle=hwnd, timeout=10) 
        win = paint_app.window(handle=hwnd)

        # Reverting to reliable win32gui focus mechanism
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(1.0) 

        # 2. MAXIMIZE THE WINDOW 
        # Alt+Space opens the window menu, then 'x' is the hotkey for Maximize
        # print("Maximizing window for predictable coordinates...")
        pyautogui.hotkey('win','alt', 'space')
        time.sleep(0.5)
        pyautogui.press('x')
        time.sleep(0.5) # Wait for maximization to complete

        # 2. Select the Rectangle Tool with a double-click check
        pyautogui.click(RECTANGLE_TOOL_X, RECTANGLE_TOOL_Y)
        time.sleep(0.5)
        
        # 3. Clear any active selection (Esc key) just in case
        pyautogui.press('esc')
        time.sleep(0.5)

        # 4. Move the mouse to the starting position on the canvas
        pyautogui.moveTo(CANVAS_START_X, CANVAS_START_Y, duration=0.2)
        pyautogui.click()
        time.sleep(0.5) # PAUSE to ensure mouse is in place

        # 6. Drag the mouse to the end position
        start_x = CANVAS_START_X + x1
        start_y = CANVAS_START_Y + y1

        end_x = start_x + x2
        end_y = start_y + y2
        
        # Draw the shape with smoother movements
        pyautogui.moveTo(start_x, start_y, duration=0.2)
        time.sleep(0.2)
        pyautogui.mouseDown()
        time.sleep(0.2)
        pyautogui.moveTo(end_x, end_y, duration=0.5)
        time.sleep(0.2)
        pyautogui.mouseUp()

        pyautogui.moveTo(CANVAS_START_X, CANVAS_START_Y, duration=0.2)
        pyautogui.click()
        time.sleep(0.5) # PAUSE to ensure mouse is in place
    
    except Exception as e:
        # print(f"Error during drawing operation: {str(e)}")
        return f"Error during drawing operation: {str(e)}"
        

def add_text_in_paint(hwnd: int, text: str, x: int, y: int):
    """
    Blocking function that performs the actual drawing using pywinauto/win32gui.
    """
    hwnd = int(hwnd)
    
    # 1. Activate and Focus the Paint window
    try:
        # Connect to Paint window, ensuring we use the UIA backend for reliable ribbon access.
        paint_app = Application(backend="uia").connect(handle=hwnd, timeout=10) 
        win = paint_app.window(handle=hwnd)

        # Reverting to reliable win32gui focus mechanism
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        
        # FIX 1: Removed wait_for_idle and increased sleep for stabilization
        time.sleep(1.0) 

        # 2. MAXIMIZE THE WINDOW 
        # Alt+Space opens the window menu, then 'x' is the hotkey for Maximize
        # print("Maximizing window for predictable coordinates...")
        pyautogui.hotkey('win','alt', 'space')
        time.sleep(0.5)
        pyautogui.press('x')
        time.sleep(0.5) # Wait for maximization to complete

        # 2. Select the Text Tool with a double-click check
        pyautogui.click(TEXT_TOOL_X, TEXT_TOOL_Y)
        time.sleep(0.5)
        
        # 3. Clear any active selection (Esc key) just in case
        pyautogui.press('esc')
        time.sleep(0.5)

        # 4. Move the mouse to the starting position on the canvas
        pyautogui.moveTo(CANVAS_START_X, CANVAS_START_Y, duration=0.2)
        pyautogui.click()
        time.sleep(0.5) # PAUSE to ensure mouse is in place
        
            
        # 6. Drag the mouse to the end position
        end_x = CANVAS_START_X + x
        end_y = CANVAS_START_Y + y
        print(f"Required text position: ({x}, {y}, adjusting to screen: ({end_x}, {end_y})")
        
               
        # 4. Move the mouse to the starting position on the canvas
        pyautogui.moveTo(end_x, end_y, duration=0.2)
        pyautogui.click()
        time.sleep(0.5) # PAUSE to ensure mouse is in place

        # 6. Command to insert the text:
        pyautogui.write(text, interval=0.05) 
        time.sleep(0.2)
        pyautogui.mouseUp()

        pyautogui.moveTo(CANVAS_START_X, CANVAS_START_Y, duration=0.2)
        pyautogui.click()
        time.sleep(0.5) # PAUSE to ensure mouse is in place


    except Exception as e:
        print(f"Error during drawing operation: {str(e)}")
        return f"Error during drawing operation: {str(e)}"
# --- MCP Tool Definitions ---

@mcp.tool()
async def draw_rectangle_tool(window_handle: int, x1: int, y1: int, x2: int, y2: int) -> dict:
    """
    Draw a visible red rectangle in MS Paint using its window handle (HWND).
    
    This tool assumes MS Paint is already open and its HWND has been provided by the open_paint tool.

    Args:
        window_handle (int): HWND of the target Paint window.
        x1, y1: Top-left corner coordinates relative to the Paint canvas (e.g., 100, 100).
        x2, y2: Bottom-right corner coordinates relative to the Paint canvas (e.g., 200, 200).
    """
    try:
        # Run the blocking GUI operation in the dedicated thread pool
        await run_in_thread(draw_red_rectangle, window_handle, x1, y1, x2, y2)
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Rectangle drawn from ({x1},{y1}) to ({x2},{y2}) in MS Paint."
                )
            ]
        }
    except Exception as e:
        # Provide a descriptive error message back to the LLM/user
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error drawing rectangle in MS Paint (HWND: {window_handle}). Ensure the window is accessible. Error details: {str(e)}"
                )
            ]
        }


@mcp.tool()
async def add_text(window_handle: int, text: str, x: int, y: int) -> dict:
    """
    Insert text in MS Paint using its window handle (HWND) at the provided coordinates.
    
    This tool assumes MS Paint is already open and its HWND has been provided by the open_paint tool.

    Args:
        window_handle (int): HWND of the target Paint window.
        x1, y1: coordinates relative to the Paint canvas from the top left corner (e.g., 100, 100).
    """
    try:
        # Run the blocking GUI operation in the dedicated thread pool
        # print(f"Adding text '{text}' at ({x},{y}) in Paint HWND: {window_handle}")
        await run_in_thread(add_text_in_paint, window_handle, text, x, y)
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Windows handle '{window_handle}', Text inserted at ({x},{y}) in MS Paint."
                )
            ]
        }
    except Exception as e:
        # Provide a descriptive error message back to the LLM/user
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error inserting text in MS Paint (HWND: {window_handle}). Ensure the window is accessible. Error details: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def open_paint() -> dict:
    """
    Open Microsoft Paint, maximize it, and try to place it on a secondary monitor (if available). 
    Returns the window handle (HWND) as a resource.
    """
    try:
        # FIX: Use UIA backend explicitly for consistency when starting
        paint_app = Application(backend="uia").start('mspaint.exe')
        time.sleep(1.0) # Give Paint more time to initialize

        # Get the Paint window spec and handle
        paint_spec = paint_app.window(class_name='MSPaintApp')
        paint_window = paint_spec.wrapper_object()
        hwnd = paint_window.handle 

        # --- Window Positioning and Sizing ---
        
        # Determine screen size (SystemMetrics(0) is primary width)
        primary_width = GetSystemMetrics(0)
        
        # Attempt to move to the secondary monitor (start X position past primary width)
        # Note: This is optional, remove if single-monitor use is expected
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOP,
            primary_width + 1, 0, # X, Y coordinates
            0, 0, # Width, Height (will be ignored by SWP_NOSIZE)
            win32con.SWP_NOSIZE
        )
        
        # Maximize the window
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        
        # FIX 3: Replaced wait_for_idle with waiting for the main window to be ready
        paint_spec.wait('ready', timeout=5)

        # Prepare JSON resource containing the HWND
        paint_window_ref = {
            "app": "mspaint",
            "window_handle": hwnd,
            "class_name": "MSPaintApp"
        }

        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Paint opened successfully (HWND: {hwnd}). It is maximized and may be on the secondary monitor."
                ),
                EmbeddedResource(
                    type="resource",
                    resource=BlobResourceContents( # FIX: Added 'resource=' here
                        uri="paint://window",
                        mimeType="application/vnd.paint.window+json",
                        blob=json.dumps(paint_window_ref).encode("utf-8")
                    )
                )
            ]
        }

    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error opening Paint application: {str(e)}"
                )
            ]
        }


# --- Server Startup ---
if __name__ == "__main__":
    # This line is essential. It starts the FastMCP server, keeping the process alive 
    # to handle incoming requests from the client via standard I/O.
    mcp.run()
