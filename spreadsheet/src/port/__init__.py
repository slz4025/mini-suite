import src.port.renderer as renderer
import src.viewer as viewer
import src.sheet as sheet


def render_cell(
    session,
    cell_position,
    render_selected=None,
    catch_failure=False,
):
    return renderer.render_cell(
      session,
      cell_position,
      render_selected,
      catch_failure,
    )


def render(session, catch_failure=False):
    upperleft = viewer.state.get_upperleft()
    nrows, ncols = viewer.state.get_dimensions()
    bounds = sheet.data.get_bounds()

    table = renderer.render_table(
        session,
        upperleft=upperleft,
        nrows=nrows,
        ncols=ncols,
        bounds=bounds,
        catch_failure=catch_failure,
    )
    return table
