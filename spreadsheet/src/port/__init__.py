import src.port.renderer as renderer
import src.port.viewer as viewer
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
    upperleft = viewer.get_upperleft(session)
    nrows, ncols = viewer.get_dimensions(session)
    bounds = sheet.get_bounds()

    table = renderer.render_table(
        session,
        upperleft=upperleft,
        nrows=nrows,
        ncols=ncols,
        bounds=bounds,
        catch_failure=catch_failure,
    )
    return table
