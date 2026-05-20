{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "e9307379-f39e-4cf3-8423-5f4380ed7f93",
   "metadata": {
    "scrolled": true
   },
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\Eason\\anaconda3\\Lib\\site-packages\\pygame\\pkgdata.py:25: UserWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html. The pkg_resources package is slated for removal as early as 2025-11-30. Refrain from using this package or pin to Setuptools<81.\n",
      "  from pkg_resources import resource_stream, resource_exists\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "pygame 2.6.1 (SDL 2.28.4, Python 3.13.9)\n",
      "Hello from the pygame community. https://www.pygame.org/contribute.html\n"
     ]
    },
    {
     "ename": "FileNotFoundError",
     "evalue": "No such file or directory: 'C:\\Users\\Eason\\Desktop\\python\\final\\battleback2nog.png'.",
     "output_type": "error",
     "traceback": [
      "\u001b[31m---------------------------------------------------------------------------\u001b[39m",
      "\u001b[31mFileNotFoundError\u001b[39m                         Traceback (most recent call last)",
      "\u001b[36mCell\u001b[39m\u001b[36m \u001b[39m\u001b[32mIn[1]\u001b[39m\u001b[32m, line 12\u001b[39m\n\u001b[32m      9\u001b[39m screen = pygame.display.set_mode((WIDTH, HEIGHT))\n\u001b[32m     10\u001b[39m pygame.display.set_caption(\u001b[33m\"\u001b[39m\u001b[33m骰子戰鬥遊戲\u001b[39m\u001b[33m\"\u001b[39m)\n\u001b[32m---> \u001b[39m\u001b[32m12\u001b[39m battle_bg = \u001b[43mpygame\u001b[49m\u001b[43m.\u001b[49m\u001b[43mimage\u001b[49m\u001b[43m.\u001b[49m\u001b[43mload\u001b[49m\u001b[43m(\u001b[49m\u001b[33;43mr\u001b[39;49m\u001b[33;43m\"\u001b[39;49m\u001b[33;43mC:\u001b[39;49m\u001b[33;43m\\\u001b[39;49m\u001b[33;43mUsers\u001b[39;49m\u001b[33;43m\\\u001b[39;49m\u001b[33;43mEason\u001b[39;49m\u001b[33;43m\\\u001b[39;49m\u001b[33;43mDesktop\u001b[39;49m\u001b[33;43m\\\u001b[39;49m\u001b[33;43mpython\u001b[39;49m\u001b[33;43m\\\u001b[39;49m\u001b[33;43mfinal\u001b[39;49m\u001b[33;43m\\\u001b[39;49m\u001b[33;43mbattleback2nog.png\u001b[39;49m\u001b[33;43m\"\u001b[39;49m\u001b[43m)\u001b[49m.convert()\n\u001b[32m     13\u001b[39m battle_bg = pygame.transform.scale(battle_bg, (WIDTH, HEIGHT))\n\u001b[32m     15\u001b[39m running = \u001b[38;5;28;01mTrue\u001b[39;00m\n",
      "\u001b[31mFileNotFoundError\u001b[39m: No such file or directory: 'C:\\Users\\Eason\\Desktop\\python\\final\\battleback2nog.png'."
     ]
    }
   ],
   "source": [
    "import pygame\n",
    "\n",
    "pygame.init()\n",
    "\n",
    "SCREEN_SIZE = [(1,480,360),(2,720,540),(3,1080,720),(4,1920,1440),(5,2880,2160)]\n",
    "SS = 2\n",
    "WIDTH, HEIGHT = int(SCREEN_SIZE[SS][1]), int(SCREEN_SIZE[SS][2])\n",
    "FPS = 60\n",
    "screen = pygame.display.set_mode((WIDTH, HEIGHT))\n",
    "pygame.display.set_caption(\"骰子戰鬥遊戲\")\n",
    "\n",
    "battle_bg = pygame.image.load(r\"C:\\Users\\Eason\\Desktop\\python\\final\\battleback2nog.png\").convert()\n",
    "battle_bg = pygame.transform.scale(battle_bg, (WIDTH, HEIGHT))\n",
    "\n",
    "running = True\n",
    "while running:\n",
    "    for event in pygame.event.get():\n",
    "        if event.type == pygame.QUIT:\n",
    "            running = False\n",
    "\n",
    "    screen.blit(battle_bg, (0, 0))\n",
    "\n",
    "    pygame.display.update()\n",
    "\n",
    "pygame.quit()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b55d5fa1-4f7f-485a-bd75-c2169dbe8123",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2f4dd9f6-717a-48c6-b440-9436f4815d40",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "753d7a40-541b-4f40-9833-f781fe5e8a21",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python [conda env:base] *",
   "language": "python",
   "name": "conda-base-py"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.9"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
