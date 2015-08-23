import asyncio
from aiohttp import web

from aot import get_board_description
from aot.api.api import Api
from aot.board import SvgBoardCreator


__all__ = ['Api', 'get_board']


@asyncio.coroutine
def get_board(request):
    name = request.match_info.get('name', 'standard')
    board_description = get_board_description(name=name)
    svg_board = SvgBoardCreator(board_description)
    return web.Response(
        body=str(svg_board).encode('utf-8'),
        headers={'Content-Type': 'image/svg+xml; charset=utf-8'})
